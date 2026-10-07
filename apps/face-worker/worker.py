"""Background CV worker loop and bounded queue for face-worker.

Interface and validation skeleton only:
- Rejects malformed or oversized input
- Bounded latest-frame per-stream queue that drops stale frames under backpressure
- Transient in-memory state only (never persists frames, crops, or templates)
- Does not fabricate matches
"""

import asyncio
import logging
import os
from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("face_worker")

# Max frame size in bytes (default 5 MB)
MAX_FRAME_SIZE_BYTES = int(os.environ.get("MAX_FRAME_SIZE_BYTES", 5 * 1024 * 1024))
# Bounded queue size per stream
QUEUE_MAXSIZE = int(os.environ.get("QUEUE_MAXSIZE", 5))

# In-memory candidate presence: {candidate_id: {"expires_at": str}}
# This scaffold does not generate templates; state is cleared on expiry or DELETE.
_candidates: Dict[str, Dict[str, Any]] = {}

# Per-stream bounded queue: {stream_id: deque(maxlen=QUEUE_MAXSIZE)}
_stream_queues: Dict[str, deque] = {}

# Worker statistics (transient counters)
_stats = {
    "frames_received": 0,
    "frames_dropped": 0,
    "frames_processed": 0,
}


def enroll_candidate(candidate_id: str, photo_bytes: bytes, expires_at: str) -> None:
    """Track a candidate expiry without pretending to derive a face template."""
    # This scaffold validates the photo at the API boundary but has no CV model.
    # Do not retain the reference image or create a placeholder match template.
    del photo_bytes
    _candidates[candidate_id] = {
        "expires_at": expires_at,
        "enrolled_at": datetime.now(timezone.utc).isoformat(),
    }
    # Notice: photo_bytes is NOT saved to disk or retained in memory


def remove_candidate(candidate_id: str) -> bool:
    """Remove candidate presence metadata from memory."""
    if candidate_id in _candidates:
        del _candidates[candidate_id]
        return True
    return False


def get_candidate(candidate_id: str) -> Optional[Dict[str, Any]]:
    clean_expired_candidates()
    return _candidates.get(candidate_id)


def list_candidate_ids() -> List[str]:
    clean_expired_candidates()
    return list(_candidates.keys())


def clean_expired_candidates() -> None:
    """Clean expired candidates from in-memory cohort."""
    now_iso = datetime.now(timezone.utc).isoformat()
    expired = [
        cid for cid, data in _candidates.items()
        if data.get("expires_at") and data["expires_at"] < now_iso
    ]
    for cid in expired:
        del _candidates[cid]


def validate_frame(frame_bytes: bytes) -> Tuple[bool, Optional[str]]:
    """Validate incoming frame size and JPEG markers.

    Returns (is_valid, error_message).
    """
    if len(frame_bytes) > MAX_FRAME_SIZE_BYTES:
        return False, f"Frame size {len(frame_bytes)} exceeds maximum limit {MAX_FRAME_SIZE_BYTES}"

    if len(frame_bytes) < 4:
        return False, "Frame payload too small to be a valid image"

    # Validate JPEG SOI (Start Of Image) marker 0xFF 0xD8
    if not (frame_bytes[0] == 0xFF and frame_bytes[1] == 0xD8):
        return False, "Malformed JPEG frame: missing Start Of Image marker (0xFFD8)"

    # Validate JPEG EOI (End Of Image) marker 0xFF 0xD9
    if not (frame_bytes[-2] == 0xFF and frame_bytes[-1] == 0xD9):
        return False, "Malformed JPEG frame: missing End Of Image marker (0xFFD9)"

    return True, None


def enqueue_frame(
    stream_id: str,
    device_id: Optional[str],
    sequence: int,
    captured_at: str,
    frame_bytes: bytes,
) -> bool:
    """Enqueue frame into bounded per-stream queue.

    If queue is at capacity, the oldest frame is dropped to prevent latency buildup.
    """
    if stream_id not in _stream_queues:
        _stream_queues[stream_id] = deque(maxlen=QUEUE_MAXSIZE)

    q = _stream_queues[stream_id]
    if len(q) >= QUEUE_MAXSIZE:
        _stats["frames_dropped"] += 1

    _stats["frames_received"] += 1
    # Store transient frame tuple: (device_id, stream_id, sequence, captured_at, frame_bytes)
    q.append((device_id, stream_id, sequence, captured_at, frame_bytes))
    return True


async def cv_worker_loop():
    """Background CV processing loop.

    Pulls frames from per-stream queues, checks candidate cohort,
    and transiently processes frames without fabricating matches.
    """
    while True:
        try:
            processed_any = False
            for stream_id, q in list(_stream_queues.items()):
                if q:
                    device_id, s_id, seq, captured_at, frame_bytes = q.popleft()
                    _stats["frames_processed"] += 1
                    processed_any = True

                    # Skeleton: inspect frame bounds, discard payload immediately.
                    # As an interface/validation skeleton, we explicitly do NOT fabricate matches.
                    del frame_bytes
                    if not q:
                        _stream_queues.pop(stream_id, None)

            # Periodic cleanup
            clean_expired_candidates()

            if not processed_any:
                await asyncio.sleep(0.05)
            else:
                await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Error in CV worker loop: %s", e)
            await asyncio.sleep(0.1)


def get_stats() -> Dict[str, Any]:
    return {
        **_stats,
        "active_candidates": len(_candidates),
        "active_streams": len(_stream_queues),
    }
