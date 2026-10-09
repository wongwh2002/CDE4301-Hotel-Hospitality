"""One-shot frame replay for Hotel Smart-Glasses POC.

Sends a prepared synthetic or consented frame fixture once through the
real lounge-control device WebSocket interface and exits.
Never logs or persists frame payloads.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional
import websockets

# Ensure local module directory and repo root are in path
MODULE_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODULE_DIR.parent.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from contracts.models import DeviceStreamMessage, utc_now_iso
from fixtures.synthetic_data import SYNTHETIC_FACE_JPEG_BYTES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("frame_replay")

DEFAULT_WS_URL = os.environ.get("WS_URL", "ws://lounge-control:8000")
DEFAULT_DEVICE_ID = os.environ.get("DEVICE_ID", "device-replay-1")
DEFAULT_STREAM_ID = os.environ.get("STREAM_ID", "stream-replay-1")
DEFAULT_TOKEN = os.environ.get("DEVICE_AUTH_TOKEN", "")


def load_fixture(fixture_path: Optional[str]) -> bytes:
    """Load the requested fixture, or use the embedded synthetic test image."""
    if fixture_path:
        p = Path(fixture_path)
        if not p.is_file():
            raise FileNotFoundError(f"Fixture does not exist: {p}")
        data = p.read_bytes()
        if not data:
            raise ValueError(f"Fixture is empty: {p}")
        return data
    return SYNTHETIC_FACE_JPEG_BYTES


async def run_replay(
    ws_url: str,
    device_id: str,
    stream_id: str,
    token: str,
    fixture_path: Optional[str],
    frame_count: int,
    interval: float,
    wait_response: float,
) -> int:
    """Execute one-shot frame replay over device WebSocket and exit."""
    frame_bytes = load_fixture(fixture_path)
    logger.info("Loaded synthetic fixture: %d bytes (never logged or persisted)", len(frame_bytes))

    url = f"{ws_url.rstrip('/')}/v1/devices/{device_id}/stream?token={token}"
    logger.info("Connecting to lounge-control: %s/v1/devices/%s/stream", ws_url, device_id)

    try:
        async with websockets.connect(url) as ws:
            # 1. Read initial session ack
            try:
                ack_raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
                logger.info("Server session ack: %s", ack_raw)
            except asyncio.TimeoutError:
                logger.info("No session ack received, proceeding with frame replay")

            # 2. Transmit frame sequence
            for seq in range(1, frame_count + 1):
                captured_at = utc_now_iso()
                meta = DeviceStreamMessage(
                    type="frame_meta",
                    stream_id=stream_id,
                    device_id=device_id,
                    sequence=seq,
                    captured_at=captured_at,
                    format="image/jpeg",
                )

                # Send metadata JSON followed by binary JPEG payload
                await ws.send(meta.model_dump_json())
                await ws.send(frame_bytes)
                logger.info(
                    "Replayed frame %d/%d: stream=%s, bytes=%d, captured_at=%s",
                    seq, frame_count, stream_id, len(frame_bytes), captured_at,
                )

                if seq < frame_count and interval > 0:
                    await asyncio.sleep(interval)

            # 3. Wait briefly for potential server cue / status messages
            logger.info("Listening for cues/events (timeout=%.1fs)...", wait_response)
            try:
                while True:
                    response = await asyncio.wait_for(ws.recv(), timeout=wait_response)
                    logger.info("Received from lounge-control: %s", response)
            except asyncio.TimeoutError:
                logger.info("Wait window finished; no further messages")

            logger.info("One-shot frame replay completed successfully")
            return 0

    except Exception as e:
        logger.error("Frame replay encountered error: %s", e)
        return 1


def main():
    parser = argparse.ArgumentParser(description="One-shot frame replay for Hotel POC")
    parser.add_argument("--ws-url", default=DEFAULT_WS_URL, help="Base WebSocket URL")
    parser.add_argument("--device-id", default=DEFAULT_DEVICE_ID, help="Companion device ID")
    parser.add_argument("--stream-id", default=DEFAULT_STREAM_ID, help="Camera stream ID")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Device auth token")
    parser.add_argument("--fixture", default=None, help="Path to synthetic/consented JPEG fixture")
    parser.add_argument(
        "--frames",
        type=int,
        default=3,
        help="Number of frames to send (default: 3 for stable-match confirmation)",
    )
    parser.add_argument("--interval", type=float, default=0.1, help="Interval between frames (s)")
    parser.add_argument("--wait-response", type=float, default=1.0, help="Seconds to listen before exit")

    args = parser.parse_args()

    exit_code = asyncio.run(run_replay(
        ws_url=args.ws_url,
        device_id=args.device_id,
        stream_id=args.stream_id,
        token=args.token,
        fixture_path=args.fixture,
        frame_count=args.frames,
        interval=args.interval,
        wait_response=args.wait_response,
    ))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
