"""Transient face matching and bounded frame processing for face-worker."""

import asyncio
import logging
import os
from pathlib import Path
import sys
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List, Optional, Tuple

import httpx

# Allow the module's explicit file-based unit-test loader to find this sibling.
MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

from vision import FaceCountError, InvalidImage

logger = logging.getLogger("face_worker")

MAX_FRAME_SIZE_BYTES = int(os.environ.get("MAX_FRAME_SIZE_BYTES", 5 * 1024 * 1024))
QUEUE_MAXSIZE = int(os.environ.get("QUEUE_MAXSIZE", 5))
MATCH_THRESHOLD = float(os.environ.get("FACE_MATCH_THRESHOLD", "0.50"))
MATCH_MARGIN = float(os.environ.get("FACE_MATCH_MARGIN", "0.10"))
STABLE_FRAME_COUNT = max(2, int(os.environ.get("FACE_STABLE_FRAMES", "3")))
TRACK_MAX_MISSES = 3
TRACK_TTL_SECONDS = 2.5


@dataclass
class CandidateState:
    expires_at: datetime
    embedding: Any = None
    template_status: str = "unavailable"


@dataclass
class FaceTrack:
    track_id: str
    bbox: Tuple[float, float, float, float]
    last_seen: float
    evidence: Deque[Optional[str]] = field(default_factory=deque)
    emitted_candidate: Optional[str] = None
    last_score: Optional[float] = None
    misses: int = 0


_candidates: Dict[str, CandidateState] = {}
_stream_queues: Dict[str, deque] = {}
_tracks: Dict[str, Dict[str, FaceTrack]] = {}
_face_engine: Any = None
_stats = {"frames_received": 0, "frames_dropped": 0, "frames_processed": 0}


def set_face_engine(engine: Any) -> None:
    """Set the model implementation; exposed for isolated tests and startup."""
    global _face_engine
    _face_engine = engine


def get_face_engine() -> Any:
    return _face_engine


def _parse_expiry(expires_at: str) -> datetime:
    parsed = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def enroll_candidate(candidate_id: str, photo_bytes: bytes, expires_at: str) -> str:
    """Derive and retain only a single face embedding, never the source photo."""
    embedding = None
    template_status = "recognition_disabled"
    if _face_engine is not None and photo_bytes:
        try:
            embedding = _face_engine.create_template(photo_bytes)
            template_status = "ready"
        except FaceCountError:
            template_status = "no_single_face"
        except InvalidImage:
            raise

    _candidates[candidate_id] = CandidateState(
        expires_at=_parse_expiry(expires_at),
        embedding=embedding,
        template_status=template_status,
    )
    return template_status


def remove_candidate(candidate_id: str) -> bool:
    """Remove a candidate embedding from transient memory."""
    existed = _candidates.pop(candidate_id, None) is not None
    return existed


def get_candidate(candidate_id: str) -> Optional[Dict[str, Any]]:
    clean_expired_candidates()
    candidate = _candidates.get(candidate_id)
    if not candidate:
        return None
    return {
        "expires_at": candidate.expires_at.isoformat(),
        "template_status": candidate.template_status,
    }


def list_candidate_ids() -> List[str]:
    clean_expired_candidates()
    return list(_candidates.keys())


def clean_expired_candidates() -> None:
    """Delete expired embeddings from memory."""
    now = datetime.now(timezone.utc)
    expired = [cid for cid, item in _candidates.items() if item.expires_at <= now]
    for candidate_id in expired:
        remove_candidate(candidate_id)


def validate_frame(frame_bytes: bytes) -> Tuple[bool, Optional[str]]:
    """Check payload bounds and JPEG start/end markers."""
    if len(frame_bytes) > MAX_FRAME_SIZE_BYTES:
        return False, f"Frame size {len(frame_bytes)} exceeds maximum limit {MAX_FRAME_SIZE_BYTES}"
    if len(frame_bytes) < 4:
        return False, "Frame payload too small to be a valid image"
    if frame_bytes[:2] != b"\xff\xd8":
        return False, "Malformed JPEG frame: missing Start Of Image marker (0xFFD8)"
    if frame_bytes[-2:] != b"\xff\xd9":
        return False, "Malformed JPEG frame: missing End Of Image marker (0xFFD9)"
    return True, None


def enqueue_frame(
    stream_id: str,
    device_id: Optional[str],
    sequence: int,
    captured_at: str,
    frame_bytes: bytes,
) -> bool:
    """Queue a transient JPEG, dropping the oldest payload on backpressure."""
    if stream_id not in _stream_queues:
        _stream_queues[stream_id] = deque(maxlen=QUEUE_MAXSIZE)
    queue = _stream_queues[stream_id]
    if len(queue) >= QUEUE_MAXSIZE:
        _stats["frames_dropped"] += 1
    _stats["frames_received"] += 1
    queue.append((device_id, stream_id, sequence, captured_at, frame_bytes))
    return True


def _intersection_over_union(
    left: Tuple[float, float, float, float], right: Tuple[float, float, float, float]
) -> float:
    lx, ly, lw, lh = left
    rx, ry, rw, rh = right
    x1, y1 = max(lx, rx), max(ly, ry)
    x2, y2 = min(lx + lw, rx + rw), min(ly + lh, ry + rh)
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    union = lw * lh + rw * rh - intersection
    return intersection / union if union > 0 else 0.0


def _best_candidate(embedding: Any) -> tuple[Optional[str], Optional[float]]:
    if _face_engine is None:
        return None, None
    matches = []
    for candidate_id, candidate in _candidates.items():
        if candidate.embedding is None:
            continue
        score = _face_engine.cosine_similarity(embedding, candidate.embedding)
        matches.append((candidate_id, score))
    matches.sort(key=lambda item: item[1], reverse=True)
    if not matches or matches[0][1] < MATCH_THRESHOLD:
        return None, matches[0][1] if matches else None
    if len(matches) > 1 and matches[0][1] - matches[1][1] < MATCH_MARGIN:
        return None, matches[0][1]
    return matches[0]


def _new_event(
    stream_id: str,
    device_id: Optional[str],
    track: FaceTrack,
    status: str,
    candidate_id: Optional[str],
) -> Dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "device_id": device_id,
        "stream_id": stream_id,
        "track_id": track.track_id,
        "status": status,
        "confidence": track.last_score if status == "stable_match" else None,
        "matched_at": datetime.now(timezone.utc).isoformat(),
    }


def _process_frame(
    device_id: Optional[str], stream_id: str, detections: list[Any]
) -> list[Dict[str, Any]]:
    """Associate model detections and stabilize matches on the event loop."""
    clean_expired_candidates()
    now = time.monotonic()
    stream_tracks = _tracks.setdefault(stream_id, {})
    events: list[Dict[str, Any]] = []
    assigned_track_ids: set[str] = set()

    for detection in detections:
        possible = [
            (track_id, track)
            for track_id, track in stream_tracks.items()
            if track_id not in assigned_track_ids and now - track.last_seen <= TRACK_TTL_SECONDS
        ]
        best = max(
            possible,
            key=lambda pair: _intersection_over_union(pair[1].bbox, detection.bbox),
            default=None,
        )
        if best and _intersection_over_union(best[1].bbox, detection.bbox) >= 0.10:
            track = best[1]
        else:
            track = FaceTrack(
                track_id=f"track-{uuid.uuid4().hex[:12]}",
                bbox=detection.bbox,
                last_seen=now,
                evidence=deque(maxlen=STABLE_FRAME_COUNT),
            )
            stream_tracks[track.track_id] = track

        assigned_track_ids.add(track.track_id)
        track.bbox = detection.bbox
        track.last_seen = now
        candidate_id, score = _best_candidate(detection.embedding)
        track.last_score = score
        track.misses = 0 if candidate_id else track.misses + 1
        track.evidence.append(candidate_id)

        is_stable = (
            candidate_id is not None
            and len(track.evidence) == STABLE_FRAME_COUNT
            and all(item == candidate_id for item in track.evidence)
        )
        if is_stable and track.emitted_candidate != candidate_id:
            track.emitted_candidate = candidate_id
            events.append(_new_event(stream_id, device_id, track, "stable_match", candidate_id))
        elif track.emitted_candidate and track.misses >= TRACK_MAX_MISSES:
            track.emitted_candidate = None
            events.append(_new_event(stream_id, device_id, track, "no_match", None))

    for track_id, track in list(stream_tracks.items()):
        if track_id in assigned_track_ids:
            continue
        track.misses += 1
        track.evidence.append(None)
        if track.emitted_candidate and track.misses >= TRACK_MAX_MISSES:
            track.emitted_candidate = None
            events.append(_new_event(stream_id, device_id, track, "no_match", None))
        if now - track.last_seen > TRACK_TTL_SECONDS:
            if track.emitted_candidate:
                track.emitted_candidate = None
                events.append(_new_event(stream_id, device_id, track, "no_match", None))
            stream_tracks.pop(track_id, None)

    if not stream_tracks:
        _tracks.pop(stream_id, None)
    return events


def _expire_tracks() -> list[Dict[str, Any]]:
    """Clear cues and discard track state after a stream goes quiet."""
    now = time.monotonic()
    events = []
    for stream_id, tracks in list(_tracks.items()):
        for track_id, track in list(tracks.items()):
            if now - track.last_seen <= TRACK_TTL_SECONDS:
                continue
            if track.emitted_candidate:
                events.append(_new_event(stream_id, None, track, "no_match", None))
            tracks.pop(track_id, None)
        if not tracks:
            _tracks.pop(stream_id, None)
    return events


async def _report_events(client: httpx.AsyncClient, events: list[Dict[str, Any]]) -> None:
    if not events:
        return
    lounge_url = os.environ.get("LOUNGE_CONTROL_URL", "http://lounge-control:8000").rstrip("/")
    internal_token = os.environ.get("INTERNAL_API_TOKEN", "")
    for event in events:
        try:
            response = await client.post(
                f"{lounge_url}/internal/v1/matches",
                json={key: value for key, value in event.items() if value is not None},
                headers={"X-Internal-Token": internal_token},
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Could not deliver recognition result to lounge-control: %s", exc)


async def cv_worker_loop() -> None:
    """Process each stream's newest queued JPEG without blocking the API loop."""
    async with httpx.AsyncClient(timeout=3.0) as client:
        while True:
            try:
                processed_any = False
                for stream_id, queue in list(_stream_queues.items()):
                    if not queue:
                        continue
                    device_id, _, sequence, captured_at, frame_bytes = queue.popleft()
                    if not queue:
                        _stream_queues.pop(stream_id, None)
                    engine = _face_engine
                    try:
                        detections = (
                            await asyncio.to_thread(engine.detect, frame_bytes)
                            if engine is not None
                            else []
                        )
                    except InvalidImage:
                        detections = []
                    events = _process_frame(device_id, stream_id, detections)
                    _stats["frames_processed"] += 1
                    processed_any = True
                    del frame_bytes
                    await _report_events(client, events)

                clean_expired_candidates()
                await _report_events(client, _expire_tracks())
                if not processed_any:
                    await asyncio.sleep(0.05)
                else:
                    await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in face recognition worker loop")
                await asyncio.sleep(0.1)


def get_stats() -> Dict[str, Any]:
    return {
        **_stats,
        "active_candidates": len(_candidates),
        "recognition_ready_candidates": sum(
            candidate.embedding is not None for candidate in _candidates.values()
        ),
        "active_streams": len(_stream_queues),
        "face_engine_ready": _face_engine is not None,
    }
