#!/usr/bin/env python3
"""Measure one face-worker through the real lounge-control WebSocket.

The JSON report contains timings and per-frame detection/match counts only. It
never writes image bytes, crops, names, candidate IDs, embeddings, or input paths.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import sys
import time
import uuid

import httpx
import websockets

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from contracts.models import utc_now_iso  # noqa: E402


def percentile(values: list[float], percent: float) -> float | None:
    """Return the nearest-rank percentile or None when no values were measured."""
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(percent / 100 * len(ordered)) - 1)
    return round(ordered[index], 3)


def timing_summary(values: list[float]) -> dict[str, float | None]:
    return {
        "p50_ms": percentile(values, 50),
        "p95_ms": percentile(values, 95),
        "mean_ms": round(statistics.fmean(values), 3) if values else None,
    }


def throughput_metrics(
    processed_count: int,
    stream_started: float,
    send_finished: float,
    result_arrivals: dict[int, float],
) -> tuple[float, float]:
    """Measure delivered frames per second until the last processed result."""
    latest_result = max(result_arrivals.values(), default=send_finished)
    duration = max(0.001, max(send_finished, latest_result) - stream_started)
    return round(processed_count / duration, 3), round(duration, 3)


def _parse_reference(value: str) -> tuple[str, Path]:
    candidate_id, separator, path = value.partition("=")
    if not separator or not candidate_id or not path:
        raise argparse.ArgumentTypeError("reference must be candidate-id=photo.jpg")
    return candidate_id, Path(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default="run")
    parser.add_argument("--ws-url", default="ws://127.0.0.1:8003")
    parser.add_argument("--worker-url", default="http://127.0.0.1:8001")
    parser.add_argument("--device-id", default="m1-benchmark-device")
    parser.add_argument("--frame", action="append", type=Path, required=True)
    parser.add_argument("--reference", action="append", type=_parse_reference, default=[])
    parser.add_argument("--frames", type=int, default=20)
    parser.add_argument("--interval-seconds", type=float, default=0.5)
    parser.add_argument("--result-timeout-seconds", type=float, default=90.0)
    parser.add_argument("--report-out", type=Path)
    parser.add_argument("--token", default=os.environ.get("DEVICE_AUTH_TOKEN", ""))
    parser.add_argument("--internal-token", default=os.environ.get("INTERNAL_API_TOKEN", ""))
    args = parser.parse_args()
    if args.frames < 1 or args.interval_seconds < 0:
        parser.error("--frames must be positive and --interval-seconds cannot be negative")
    if not args.token or not args.internal_token:
        parser.error("load DEVICE_AUTH_TOKEN and INTERNAL_API_TOKEN from your local .env")
    return args


def load_frames(paths: list[Path]) -> tuple[list[bytes], list[str]]:
    frames = []
    fingerprints = []
    for path in paths:
        suffix = path.suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".jxl", ".png"}:
            raise ValueError(f"Unsupported benchmark frame extension: {path.suffix}")
        payload = path.read_bytes()
        if not payload:
            raise ValueError("A benchmark frame is empty")
        if suffix == ".png":
            import cv2
            import numpy as np

            image = cv2.imdecode(
                np.frombuffer(payload, dtype=np.uint8), cv2.IMREAD_COLOR
            )
            if image is None or image.size == 0:
                raise ValueError("A PNG benchmark frame could not be decoded")
            success, encoded = cv2.imencode(
                ".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            )
            if not success:
                raise ValueError("A PNG benchmark frame could not be encoded as JPEG")
            payload = encoded.tobytes()
        frames.append(payload)
        fingerprints.append(hashlib.sha256(payload).hexdigest())
    return frames, fingerprints


def _health(url: str) -> dict:
    response = httpx.get(f"{url.rstrip('/')}/health", timeout=5.0)
    response.raise_for_status()
    return response.json()


def _enroll_references(worker_url: str, token: str, references) -> None:
    headers = {"X-Internal-Token": token}
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
    for candidate_id, path in references:
        photo = path.read_bytes()
        payload = {
            "candidate_id": candidate_id,
            "expires_at": expires_at,
            "photo_b64": base64.b64encode(photo).decode("ascii"),
        }
        response = httpx.put(
            f"{worker_url.rstrip('/')}/internal/v1/candidates/{candidate_id}",
            json=payload,
            headers=headers,
            timeout=60.0,
        )
        response.raise_for_status()


def _content_type(path: Path) -> str:
    return "image/jxl" if path.suffix.lower() == ".jxl" else "image/jpeg"


async def run_benchmark(args: argparse.Namespace) -> dict:
    frames, frame_hashes = load_frames(args.frame)
    reference_hashes = [
        hashlib.sha256(path.read_bytes()).hexdigest()
        for _, path in args.reference
    ]
    _enroll_references(args.worker_url, args.internal_token, args.reference)
    health_before = await asyncio.to_thread(_health, args.worker_url)
    ws_url = (
        f"{args.ws_url.rstrip('/')}/v1/video/stream/"
        f"{args.device_id}"
    )
    stream_id = f"m1-benchmark-{uuid.uuid4().hex[:12]}"
    received: dict[int, dict] = {}
    send_started: dict[int, float] = {}
    lounge_forward: dict[int, float] = {}
    result_arrived: dict[int, float] = {}
    final_sequence = args.frames
    done = asyncio.Event()

    async with websockets.connect(
        ws_url,
        subprotocols=["device-stream-v1", f"device-token.{args.token}"],
        max_size=8 * 1024 * 1024,
    ) as socket:
        ack = json.loads(await asyncio.wait_for(socket.recv(), timeout=5.0))
        if ack.get("type") != "session_ack":
            raise RuntimeError("lounge-control did not acknowledge the benchmark session")

        async def receive_results() -> None:
            while not done.is_set():
                try:
                    raw = await asyncio.wait_for(socket.recv(), timeout=0.5)
                except asyncio.TimeoutError:
                    continue
                message = json.loads(raw)
                sequence = message.get("sequence")
                if message.get("type") == "debug_timing" and sequence is not None:
                    lounge_forward[int(sequence)] = float(
                        message.get("lounge_forward_ms", 0.0)
                    )
                elif (
                    message.get("type") == "debug_frame"
                    and sequence is not None
                    and int(sequence) not in received
                ):
                    sequence = int(sequence)
                    # Retain only count and timings; discard all crop/image bytes.
                    faces = message.get("faces", [])
                    received[sequence] = {
                        "sequence": sequence,
                        "face_count": len(faces),
                        "matched_face_count": sum(
                            bool(face.get("candidate_match")) for face in faces
                        ),
                        "queue_wait_ms": float(message.get("queue_wait_ms", 0.0)),
                        "detect_ms": float(message.get("detect_ms", 0.0)),
                        "association_ms": float(message.get("association_ms", 0.0)),
                    }
                    result_arrived[sequence] = time.perf_counter()
                    if len(received) >= final_sequence:
                        done.set()

        receiver = asyncio.create_task(receive_results())
        started = time.perf_counter()
        for sequence in range(1, args.frames + 1):
            source_index = (sequence - 1) % len(frames)
            source_path = args.frame[source_index]
            send_started[sequence] = time.perf_counter()
            metadata = {
                "type": "frame_meta",
                "stream_id": stream_id,
                "device_id": args.device_id,
                "sequence": sequence,
                "captured_at": utc_now_iso(),
                "format": _content_type(source_path),
                "debug_faces": True,
            }
            await socket.send(json.dumps(metadata))
            await socket.send(frames[source_index])
            if sequence < args.frames and args.interval_seconds:
                await asyncio.sleep(args.interval_seconds)

        send_finished = time.perf_counter()
        try:
            await asyncio.wait_for(done.wait(), timeout=args.result_timeout_seconds)
        except asyncio.TimeoutError:
            pass
        stream_finished = time.perf_counter()
        receiver.cancel()
        await asyncio.gather(receiver, return_exceptions=True)

    health_after = await asyncio.to_thread(_health, args.worker_url)
    per_frame = []
    for sequence in sorted(received):
        row = received[sequence]
        row["client_result_ms"] = round(
            (result_arrived[sequence] - send_started[sequence]) * 1000, 3
        )
        forward_ms = lounge_forward.get(sequence)
        row["lounge_forward_ms"] = (
            round(forward_ms, 3) if forward_ms is not None else None
        )
        per_frame.append(row)

    detect_times = [row["detect_ms"] for row in per_frame]
    result_times = [row["client_result_ms"] for row in per_frame]
    lounge_times = [
        row["lounge_forward_ms"]
        for row in per_frame
        if row["lounge_forward_ms"] is not None
    ]
    processed_count = len(per_frame)
    frames_per_second, processing_duration = throughput_metrics(
        processed_count, started, send_finished, result_arrived
    )
    stats = (
        "frames_received",
        "frames_dropped",
        "frames_dropped_stale",
        "frames_dropped_out_of_order",
        "frames_processed",
    )
    health_delta = {
        key: max(0, int(health_after.get(key, 0)) - int(health_before.get(key, 0)))
        for key in stats
    }
    return {
        "schema": "m1-face-worker-benchmark/v1",
        "label": args.label,
        "runtime": {
            "requested_execution_provider": health_after.get(
                "requested_execution_provider"
            ),
            "model_runtime": health_after.get("model_runtime"),
            "service_startup_ms": health_after.get("service_startup_ms"),
            "model_initialization_ms": health_after.get("model_initialization_ms"),
            "model_cache_warm_at_start": health_after.get(
                "model_cache_warm_at_start"
            ),
            "match_threshold": health_after.get("match_threshold"),
            "match_margin": health_after.get("match_margin"),
            "stable_frame_count": health_after.get("stable_frame_count"),
            "stable_match_count": health_after.get("stable_match_count"),
        },
        "workload": {
            "model": "buffalo_l",
            "frame_count_requested": args.frames,
            "frame_interval_seconds": args.interval_seconds,
            "frame_sha256": frame_hashes,
            "reference_sha256": reference_hashes,
        },
        "results": {
            "frames_sent": args.frames,
            "frames_returned": processed_count,
            "frames_missing": args.frames - processed_count,
            "frames_per_second": frames_per_second,
            "send_duration_seconds": round(send_finished - started, 3),
            "processing_duration_seconds": processing_duration,
            "result_drain_wait_seconds": round(stream_finished - send_finished, 3),
            "worker_detect": timing_summary(detect_times),
            "client_capture_to_result": timing_summary(result_times),
            "lounge_forward": timing_summary(lounge_times),
            "health_counter_delta": health_delta,
            "per_frame": per_frame,
        },
    }


def main() -> int:
    args = parse_args()
    report = asyncio.run(run_benchmark(args))
    serialized = json.dumps(report, indent=2, sort_keys=True)
    if args.report_out:
        args.report_out.write_text(serialized + "\n")
        print(f"Wrote sanitized benchmark report: {args.report_out}")
    else:
        print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
