"""Transient face matching and bounded frame processing for face-worker."""

import asyncio
import base64
import hashlib
import logging
import os
from pathlib import Path
import sys
from threading import RLock
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
logger.setLevel(
    getattr(logging, os.environ.get("FACE_WORKER_LOG_LEVEL", "INFO").upper(), logging.INFO)
)

MAX_FRAME_SIZE_BYTES = int(os.environ.get("MAX_FRAME_SIZE_BYTES", 5 * 1024 * 1024))
QUEUE_MAXSIZE = int(os.environ.get("QUEUE_MAXSIZE", 5))
MAX_FRAME_AGE_SECONDS = float(os.environ.get("MAX_FRAME_AGE_SECONDS", "2.0"))
MAX_FRAME_QUEUE_AGE_SECONDS = float(os.environ.get("MAX_FRAME_QUEUE_AGE_SECONDS", "1.0"))
SEQUENCE_STATE_TTL_SECONDS = 60.0
MATCH_THRESHOLD = float(os.environ.get("FACE_MATCH_THRESHOLD", "0.65"))
MATCH_MARGIN = float(os.environ.get("FACE_MATCH_MARGIN", "0.10"))
STABLE_FRAME_COUNT = max(2, int(os.environ.get("FACE_STABLE_FRAMES", "3")))
STABLE_MATCH_COUNT = min(
    STABLE_FRAME_COUNT,
    max(1, int(os.environ.get("FACE_STABLE_MATCHES", "2"))),
)
TRACK_MAX_MISSES = 3
TRACK_TTL_SECONDS = 2.5
STABLE_REFRESH_INTERVAL_SECONDS = 1.0
CROP_CHANGE_HAMMING_DISTANCE = 16


@dataclass
class CandidateState:
    expires_at: datetime
    embeddings: List[Any] = field(default_factory=list)
    template_status: str = "unavailable"


@dataclass
class FaceTrack:
    track_id: str
    bbox: Tuple[float, float, float, float]
    last_seen: float
    evidence: Deque[Tuple[Optional[str], Optional[float]]] = field(default_factory=deque)
    emitted_candidate: Optional[str] = None
    last_score: Optional[float] = None
    misses: int = 0
    last_refresh_at: float = 0.0
    crop_id: Optional[str] = None
    crop_candidate_id: Optional[str] = None
    crop_signature: Optional[int] = None
    crop_b64: Optional[str] = None
    crop_pending: bool = False


_candidates: Dict[str, CandidateState] = {}
_candidates_lock = RLock()
_stream_queues: Dict[str, deque] = {}
_latest_sequences: Dict[str, int] = {}
_sequence_last_seen: Dict[str, float] = {}
_tracks: Dict[str, Dict[str, FaceTrack]] = {}
_face_engine: Any = None
_stats = {
    "frames_received": 0,
    "frames_dropped": 0,
    "frames_dropped_stale": 0,
    "frames_dropped_out_of_order": 0,
    "frames_processed": 0,
}


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


def enroll_candidate(
    candidate_id: str,
    photo_bytes: bytes | List[bytes],
    expires_at: str,
) -> str:
    """Derive up to three face embeddings and retain no source photos."""
    photos = photo_bytes if isinstance(photo_bytes, list) else [photo_bytes]
    embeddings: List[Any] = []
    if _face_engine is None:
        template_status = "recognition_disabled"
    elif not photos:
        template_status = "no_reference_photos"
    else:
        for image_bytes in photos[:3]:
            if not image_bytes:
                continue
            try:
                embeddings.append(_face_engine.create_template(image_bytes))
            except FaceCountError:
                continue
            except InvalidImage:
                raise
        if embeddings:
            template_status = "ready" if len(embeddings) == len(photos) else "ready_partial"
        else:
            template_status = "no_single_face"

    with _candidates_lock:
        _candidates[candidate_id] = CandidateState(
            expires_at=_parse_expiry(expires_at),
            embeddings=embeddings,
            template_status=template_status,
        )
    return template_status


def remove_candidate(candidate_id: str) -> bool:
    """Remove a candidate embedding from transient memory."""
    with _candidates_lock:
        existed = _candidates.pop(candidate_id, None) is not None
    return existed


def get_candidate(candidate_id: str) -> Optional[Dict[str, Any]]:
    clean_expired_candidates()
    with _candidates_lock:
        candidate = _candidates.get(candidate_id)
        if candidate is None:
            return None
        return {
            "expires_at": candidate.expires_at.isoformat(),
            "template_status": candidate.template_status,
            "reference_count": len(candidate.embeddings),
        }


def list_candidate_ids() -> List[str]:
    clean_expired_candidates()
    with _candidates_lock:
        return list(_candidates.keys())


def clean_expired_candidates() -> None:
    """Delete expired embeddings from memory."""
    now = datetime.now(timezone.utc)
    with _candidates_lock:
        expired = [cid for cid, item in _candidates.items() if item.expires_at <= now]
        for candidate_id in expired:
            _candidates.pop(candidate_id, None)
    for candidate_id in expired:
        logger.info("candidate_expired candidate_id=%s", candidate_id)


def _parse_capture_time(captured_at: str) -> Optional[datetime]:
    """Parse an ISO-8601 capture time; unknown formats fall back to queue age."""
    if not captured_at:
        return None
    try:
        parsed = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _capture_age_seconds(captured_at: str) -> Optional[float]:
    """Return capture age using the laptop clock, or None when it is unknown."""
    capture_time = _parse_capture_time(captured_at)
    if capture_time is None:
        return None
    return (datetime.now(timezone.utc) - capture_time).total_seconds()


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
    sequence: Optional[int],
    captured_at: str,
    frame_bytes: bytes,
    debug_faces: bool = False,
) -> bool:
    """Queue a transient JPEG unless it is stale or older than this stream's last frame."""
    _stats["frames_received"] += 1
    now_monotonic = time.monotonic()
    expired_sequence_streams = [
        stream
        for stream, last_seen in _sequence_last_seen.items()
        if now_monotonic - last_seen > SEQUENCE_STATE_TTL_SECONDS
    ]
    for expired_stream in expired_sequence_streams:
        _sequence_last_seen.pop(expired_stream, None)
        _latest_sequences.pop(expired_stream, None)

    capture_age_seconds = _capture_age_seconds(captured_at)
    if capture_age_seconds is not None:
        if capture_age_seconds > MAX_FRAME_AGE_SECONDS:
            _stats["frames_dropped"] += 1
            _stats["frames_dropped_stale"] += 1
            logger.warning(
                "frame_rejected_stale_capture device_id=%s stream_id=%s sequence=%s "
                "frame_age_ms=%.2f max_age_ms=%.2f",
                device_id,
                stream_id,
                sequence,
                capture_age_seconds * 1000,
                MAX_FRAME_AGE_SECONDS * 1000,
            )
            return False

    if sequence is not None:
        previous_sequence = _latest_sequences.get(stream_id)
        if previous_sequence is not None and sequence <= previous_sequence:
            _stats["frames_dropped"] += 1
            _stats["frames_dropped_out_of_order"] += 1
            logger.warning(
                "frame_rejected_out_of_order device_id=%s stream_id=%s sequence=%s "
                "latest_sequence=%s",
                device_id,
                stream_id,
                sequence,
                previous_sequence,
            )
            return False
        _latest_sequences[stream_id] = sequence
    _sequence_last_seen[stream_id] = now_monotonic

    if stream_id not in _stream_queues:
        _stream_queues[stream_id] = deque(maxlen=QUEUE_MAXSIZE)
    queue = _stream_queues[stream_id]
    dropped_oldest = len(queue) >= QUEUE_MAXSIZE
    dropped_sequence = queue[0][2] if dropped_oldest else None
    if dropped_oldest:
        _stats["frames_dropped"] += 1
    queue.append(
        (device_id, stream_id, sequence, captured_at, debug_faces, now_monotonic, frame_bytes)
    )
    if dropped_oldest:
        logger.warning(
            "frame_queue_dropped_oldest device_id=%s stream_id=%s dropped_sequence=%s "
            "incoming_sequence=%s queue_capacity=%s",
            device_id,
            stream_id,
            dropped_sequence,
            sequence,
            QUEUE_MAXSIZE,
        )
    logger.debug(
        "frame_queued device_id=%s stream_id=%s sequence=%s bytes=%s queue_depth=%s/%s "
        "debug_faces=%s",
        device_id,
        stream_id,
        sequence,
        len(frame_bytes),
        len(queue),
        QUEUE_MAXSIZE,
        debug_faces,
    )
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


def _best_candidate(
    embedding: Any,
) -> tuple[Optional[str], Optional[float], Optional[str], Optional[float], str]:
    """Return the accepted candidate and score details for diagnosis."""
    if _face_engine is None:
        return None, None, None, None, "recognition_disabled"
    matches = []
    with _candidates_lock:
        candidates = list(_candidates.items())
    for candidate_id, candidate in candidates:
        if not candidate.embeddings:
            continue
        score = max(
            _face_engine.cosine_similarity(embedding, reference)
            for reference in candidate.embeddings
        )
        matches.append((candidate_id, score))
    matches.sort(key=lambda item: item[1], reverse=True)
    if not matches:
        return None, None, None, None, "no_active_reference_embeddings"

    best_candidate_id, best_score = matches[0]
    runner_up_score = matches[1][1] if len(matches) > 1 else None
    if best_score < MATCH_THRESHOLD:
        return None, best_score, best_candidate_id, runner_up_score, "below_score_threshold"
    if runner_up_score is not None and best_score - runner_up_score < MATCH_MARGIN:
        return None, best_score, best_candidate_id, runner_up_score, "insufficient_margin"
    return best_candidate_id, best_score, best_candidate_id, runner_up_score, "candidate_passed"


def _new_event(
    stream_id: str,
    device_id: Optional[str],
    track: FaceTrack,
    status: str,
    candidate_id: Optional[str],
) -> Dict[str, Any]:
    event = {
        "candidate_id": candidate_id,
        "device_id": device_id,
        "stream_id": stream_id,
        "track_id": track.track_id,
        "status": status,
        "confidence": track.last_score if status in {"stable_match", "stable_refresh"} else None,
        "matched_at": datetime.now(timezone.utc).isoformat(),
    }
    if status in {"stable_match", "stable_refresh"} and track.crop_id:
        event["crop_id"] = track.crop_id
        if track.crop_pending and track.crop_b64:
            event["crop_b64"] = track.crop_b64
    return event


def _update_track_crop(
    track: FaceTrack,
    detection: Any,
    candidate_id: Optional[str],
    force: bool = False,
) -> tuple[bool, Optional[str]]:
    """Cache a crop reference and return image data only for a new/material change."""
    if candidate_id is None:
        return False, None
    crop_jpeg = getattr(detection, "crop_jpeg", None)
    if not crop_jpeg:
        return False, None

    digest = hashlib.sha256(crop_jpeg).hexdigest()[:24]
    new_crop_id = f"crop-{digest}"
    identity_changed = track.crop_candidate_id != candidate_id
    if not force and not identity_changed and track.crop_id == new_crop_id:
        return False, None

    signature = getattr(detection, "crop_signature", None)
    if (
        not force
        and not identity_changed
        and track.crop_id is not None
        and signature is not None
        and track.crop_signature is not None
        and (signature ^ track.crop_signature).bit_count() < CROP_CHANGE_HAMMING_DISTANCE
    ):
        return False, None

    track.crop_id = new_crop_id
    track.crop_candidate_id = candidate_id
    track.crop_signature = signature
    track.crop_b64 = base64.b64encode(crop_jpeg).decode("ascii")
    track.crop_pending = True
    return True, track.crop_b64


def _stable_candidate(track: FaceTrack) -> tuple[Optional[str], Optional[float]]:
    """Return a unique candidate supported by enough votes in the full window."""
    if len(track.evidence) < STABLE_FRAME_COUNT:
        return None, None

    scores_by_candidate: Dict[str, List[float]] = {}
    for candidate_id, score in track.evidence:
        if candidate_id is not None and score is not None:
            scores_by_candidate.setdefault(candidate_id, []).append(score)

    qualifying = [
        (candidate_id, scores)
        for candidate_id, scores in scores_by_candidate.items()
        if len(scores) >= STABLE_MATCH_COUNT
    ]
    if len(qualifying) != 1:
        return None, None

    candidate_id, scores = qualifying[0]
    return candidate_id, sum(scores) / len(scores)


def _top_candidate_votes(track: FaceTrack) -> tuple[Optional[str], int]:
    votes: Dict[str, int] = {}
    for candidate_id, _ in track.evidence:
        if candidate_id is not None:
            votes[candidate_id] = votes.get(candidate_id, 0) + 1
    if not votes:
        return None, 0
    return max(votes.items(), key=lambda item: item[1])


def _track_identity_hint(track: FaceTrack) -> Optional[str]:
    """Avoid joining a new accepted identity to a track with strong other evidence."""
    if track.emitted_candidate:
        return track.emitted_candidate
    candidate_id, votes = _top_candidate_votes(track)
    return candidate_id if votes >= STABLE_MATCH_COUNT else None


def _emit_stable_event(
    device_id: Optional[str],
    stream_id: str,
    track: FaceTrack,
    now: float,
    observed_candidate_id: Optional[str],
) -> Optional[Dict[str, Any]]:
    """Emit only when this frame supports both the stable identity and its cached crop."""
    candidate_id, average_score = _stable_candidate(track)
    if candidate_id is None:
        return None
    if observed_candidate_id != candidate_id or track.crop_candidate_id != candidate_id:
        return None

    track.last_score = average_score
    if track.emitted_candidate != candidate_id:
        if not track.crop_id or not track.crop_pending:
            return None
        track.emitted_candidate = candidate_id
        track.last_refresh_at = now
        return _new_event(stream_id, device_id, track, "stable_match", candidate_id)

    if now - track.last_refresh_at >= STABLE_REFRESH_INTERVAL_SECONDS:
        track.last_refresh_at = now
        return _new_event(stream_id, device_id, track, "stable_refresh", candidate_id)
    return None


def _set_crop_delivery_state(
    stream_id: str, track_id: str, crop_id: Optional[str], delivered: bool
) -> None:
    """Keep a crop pending until lounge-control confirms phone delivery."""
    track = _tracks.get(stream_id, {}).get(track_id)
    if track is None or not crop_id or track.crop_id != crop_id:
        return
    track.crop_pending = not delivered


def _process_frame(
    device_id: Optional[str],
    stream_id: str,
    detections: list[Any],
    debug_faces: Optional[list[Dict[str, Any]]] = None,
    sequence: Optional[int] = None,
) -> list[Dict[str, Any]]:
    """Associate model detections and stabilize matches on the event loop."""
    clean_expired_candidates()
    now = time.monotonic()
    stream_tracks = _tracks.setdefault(stream_id, {})
    events: list[Dict[str, Any]] = []
    assigned_track_ids: set[str] = set()

    for detection in detections:
        candidate_id, score, top_candidate_id, runner_up_score, match_reason = (
            _best_candidate(detection.embedding)
            if detection.embedding is not None
            else (None, None, None, None, "embedding_unavailable")
        )
        possible = [
            (track_id, track, _track_identity_hint(track))
            for track_id, track in stream_tracks.items()
            if track_id not in assigned_track_ids and now - track.last_seen <= TRACK_TTL_SECONDS
        ]
        possible = [
            (track_id, track)
            for track_id, track, identity_hint in possible
            if candidate_id is None or identity_hint is None or identity_hint == candidate_id
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
        if debug_faces is not None:
            crop_jpeg = getattr(detection, "crop_jpeg", None)
            debug_face: Dict[str, Any] = {
                "track_id": track.track_id,
                "bbox": [float(value) for value in detection.bbox],
                "detector_score": float(getattr(detection, "detector_score", 0.0) or 0.0),
                "match_score": score,
                "candidate_match": candidate_id is not None,
            }
            if crop_jpeg:
                debug_face["crop_id"] = f"debug-{hashlib.sha256(crop_jpeg).hexdigest()[:24]}"
                debug_face["crop_b64"] = base64.b64encode(crop_jpeg).decode("ascii")
            debug_faces.append(debug_face)
        track.misses = 0 if candidate_id else track.misses + 1
        track.evidence.append((candidate_id, score))
        # Only cache crops from a detection that passed identity matching. This
        # keeps a different or uncertain face from replacing the stable guest's crop.
        if candidate_id is not None:
            _update_track_crop(track, detection, candidate_id)
        stable_event = _emit_stable_event(
            device_id, stream_id, track, now, candidate_id
        )
        top_vote_candidate, top_votes = _top_candidate_votes(track)
        stable_candidate, _ = _stable_candidate(track)
        if stable_event:
            decision = stable_event["status"]
        elif stable_candidate:
            decision = (
                "stable_match_already_emitted"
                if track.emitted_candidate == stable_candidate
                else "stable_vote_met_event_not_emitted"
            )
        elif len(track.evidence) < STABLE_FRAME_COUNT:
            decision = "awaiting_full_observation_window"
        elif top_votes >= STABLE_MATCH_COUNT:
            decision = "ambiguous_vote_window"
        elif top_votes:
            decision = "awaiting_more_matching_frames"
        else:
            decision = "no_candidate_passed_score_and_margin_checks"
        logger.debug(
            "identity_decision device_id=%s stream_id=%s sequence=%s track_id=%s "
            "bbox=%s detector_score=%.4f "
            "top_candidate_id=%s score=%s runner_up_score=%s match_reason=%s "
            "score_threshold=%.3f margin_required=%.3f votes=%s:%d/%d "
            "required_votes=%d decision=%s emitted_candidate_id=%s",
            device_id,
            stream_id,
            sequence,
            track.track_id,
            [float(value) for value in detection.bbox],
            float(getattr(detection, "detector_score", 0.0) or 0.0),
            top_candidate_id or "none",
            "n/a" if score is None else f"{score:.4f}",
            "n/a" if runner_up_score is None else f"{runner_up_score:.4f}",
            match_reason,
            MATCH_THRESHOLD,
            MATCH_MARGIN,
            top_vote_candidate or "none",
            top_votes,
            len(track.evidence),
            STABLE_MATCH_COUNT,
            decision,
            track.emitted_candidate or "none",
        )
        if stable_event:
            events.append(stable_event)
        elif track.emitted_candidate and track.misses >= TRACK_MAX_MISSES:
            track.emitted_candidate = None
            track.crop_id = None
            track.crop_candidate_id = None
            track.crop_signature = None
            track.crop_b64 = None
            track.crop_pending = False
            events.append(_new_event(stream_id, device_id, track, "no_match", None))

    for track_id, track in list(stream_tracks.items()):
        if track_id in assigned_track_ids:
            continue
        track.misses += 1
        track.evidence.append((None, None))
        stable_event = _emit_stable_event(device_id, stream_id, track, now, None)
        top_vote_candidate, top_votes = _top_candidate_votes(track)
        stable_candidate, _ = _stable_candidate(track)
        if stable_event:
            decision = stable_event["status"]
        elif stable_candidate:
            decision = (
                "stable_match_already_emitted"
                if track.emitted_candidate == stable_candidate
                else "stable_vote_met_event_not_emitted"
            )
        elif len(track.evidence) < STABLE_FRAME_COUNT and top_votes >= STABLE_MATCH_COUNT:
            decision = "awaiting_full_observation_window"
        elif top_votes >= STABLE_MATCH_COUNT:
            decision = "ambiguous_vote_window"
        elif top_votes:
            decision = "awaiting_more_matching_frames"
        else:
            decision = "no_matching_votes_in_window"
        logger.debug(
            "track_observation_missing device_id=%s stream_id=%s sequence=%s track_id=%s "
            "votes=%s:%d/%d required_votes=%d misses=%d decision=%s",
            device_id,
            stream_id,
            sequence,
            track.track_id,
            top_vote_candidate or "none",
            top_votes,
            len(track.evidence),
            STABLE_MATCH_COUNT,
            track.misses,
            decision,
        )
        if stable_event:
            events.append(stable_event)
        if track.emitted_candidate and track.misses >= TRACK_MAX_MISSES:
            track.emitted_candidate = None
            track.crop_id = None
            track.crop_candidate_id = None
            track.crop_signature = None
            track.crop_b64 = None
            track.crop_pending = False
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
            result = response.json()
            log_method = (
                logger.info
                if event.get("status") in {"stable_match", "no_match"}
                else logger.debug
            )
            log_method(
                "match_callback_completed device_id=%s stream_id=%s track_id=%s "
                "candidate_id=%s event_status=%s http_status=%s lounge_status=%s",
                event.get("device_id") or "unknown",
                event["stream_id"],
                event["track_id"],
                event.get("candidate_id") or "none",
                event["status"],
                response.status_code,
                result.get("status", "unknown"),
            )
            if event.get("crop_b64") and result.get("crop_delivered") is True:
                _set_crop_delivery_state(
                    event["stream_id"], event["track_id"], event.get("crop_id"), delivered=True
                )
            elif result.get("crop_required") is True:
                _set_crop_delivery_state(
                    event["stream_id"], event["track_id"], event.get("crop_id"), delivered=False
                )
        except httpx.HTTPError as exc:
            logger.warning(
                "match_callback_failed device_id=%s stream_id=%s track_id=%s "
                "event_status=%s error=%s",
                event.get("device_id") or "unknown",
                event["stream_id"],
                event["track_id"],
                event["status"],
                exc,
            )


async def _report_debug_frame(client: httpx.AsyncClient, frame: Dict[str, Any]) -> None:
    """Deliver opt-in raw detections and timings; image crops are never logged."""
    lounge_url = os.environ.get("LOUNGE_CONTROL_URL", "http://lounge-control:8000").rstrip("/")
    internal_token = os.environ.get("INTERNAL_API_TOKEN", "")
    try:
        response = await client.post(
            f"{lounge_url}/internal/v1/debug/frames",
            json=frame,
            headers={"X-Internal-Token": internal_token},
        )
        response.raise_for_status()
        logger.debug(
            "debug_frame_callback_completed device_id=%s stream_id=%s sequence=%s "
            "http_status=%s faces=%s",
            frame.get("device_id") or "unknown",
            frame["stream_id"],
            frame["sequence"],
            response.status_code,
            len(frame["faces"]),
        )
    except httpx.HTTPError as exc:
        logger.warning(
            "debug_frame_callback_failed device_id=%s stream_id=%s sequence=%s error=%s",
            frame.get("device_id") or "unknown",
            frame["stream_id"],
            frame["sequence"],
            exc,
        )


async def cv_worker_loop() -> None:
    """Process each stream's newest queued JPEG without blocking the API loop."""
    async with httpx.AsyncClient(timeout=3.0) as client:
        while True:
            try:
                processed_any = False
                for stream_id, queue in list(_stream_queues.items()):
                    if not queue:
                        continue
                    # Inference can take longer than the camera frame interval.
                    # Select the newest queued image and discard the backlog so
                    # this stream does not spend time recognizing old viewpoints.
                    stale_queued_count = len(queue) - 1
                    (
                        device_id,
                        _,
                        sequence,
                        captured_at,
                        debug_enabled,
                        enqueued_at,
                        frame_bytes,
                    ) = queue[-1]
                    queue.clear()
                    if stale_queued_count:
                        _stats["frames_dropped"] += stale_queued_count
                        _stats["frames_dropped_stale"] += stale_queued_count
                        logger.warning(
                            "frame_queue_discarded_backlog device_id=%s stream_id=%s "
                            "selected_sequence=%s dropped_count=%s",
                            device_id,
                            stream_id,
                            sequence,
                            stale_queued_count,
                        )
                    queue_wait_ms = max(0.0, (time.monotonic() - enqueued_at) * 1000)
                    _stream_queues.pop(stream_id, None)
                    if queue_wait_ms > MAX_FRAME_QUEUE_AGE_SECONDS * 1000:
                        _stats["frames_dropped"] += 1
                        _stats["frames_dropped_stale"] += 1
                        logger.warning(
                            "frame_rejected_stale_queue device_id=%s stream_id=%s sequence=%s "
                            "queue_age_ms=%.2f max_queue_age_ms=%.2f",
                            device_id,
                            stream_id,
                            sequence,
                            queue_wait_ms,
                            MAX_FRAME_QUEUE_AGE_SECONDS * 1000,
                        )
                        continue
                    capture_age_seconds = _capture_age_seconds(captured_at)
                    if (
                        capture_age_seconds is not None
                        and capture_age_seconds > MAX_FRAME_AGE_SECONDS
                    ):
                        _stats["frames_dropped"] += 1
                        _stats["frames_dropped_stale"] += 1
                        logger.warning(
                            "frame_rejected_stale_before_inference device_id=%s stream_id=%s "
                            "sequence=%s frame_age_ms=%.2f max_age_ms=%.2f",
                            device_id,
                            stream_id,
                            sequence,
                            capture_age_seconds * 1000,
                            MAX_FRAME_AGE_SECONDS * 1000,
                        )
                        continue
                    engine = _face_engine
                    logger.debug(
                        "frame_processing_started device_id=%s stream_id=%s sequence=%s "
                        "bytes=%s queue_wait_ms=%.2f model_ready=%s debug_faces=%s",
                        device_id,
                        stream_id,
                        sequence,
                        len(frame_bytes),
                        queue_wait_ms,
                        engine is not None,
                        debug_enabled,
                    )
                    detect_started = time.perf_counter()
                    try:
                        logger.debug(
                            "face_detection_started device_id=%s stream_id=%s sequence=%s",
                            device_id,
                            stream_id,
                            sequence,
                        )
                        detections = (
                            await asyncio.to_thread(engine.detect, frame_bytes)
                            if engine is not None
                            else []
                        )
                    except InvalidImage as exc:
                        logger.warning(
                            "face_detection_rejected_invalid_image device_id=%s stream_id=%s "
                            "sequence=%s error=%s",
                            device_id,
                            stream_id,
                            sequence,
                            exc,
                        )
                        detections = []
                    except Exception as exc:
                        raise RuntimeError(
                            "face_detection_failed "
                            f"device_id={device_id} stream_id={stream_id} sequence={sequence}"
                        ) from exc
                    detect_ms = (time.perf_counter() - detect_started) * 1000
                    logger.debug(
                        "face_detection_completed device_id=%s stream_id=%s sequence=%s "
                        "faces=%s detect_ms=%.2f",
                        device_id,
                        stream_id,
                        sequence,
                        len(detections),
                        detect_ms,
                    )
                    debug_detections: Optional[list[Dict[str, Any]]] = [] if debug_enabled else None
                    association_started = time.perf_counter()
                    events = _process_frame(
                        device_id,
                        stream_id,
                        detections,
                        debug_faces=debug_detections,
                        sequence=sequence,
                    )
                    association_ms = (time.perf_counter() - association_started) * 1000
                    processing_ms = queue_wait_ms + detect_ms + association_ms
                    _stats["frames_processed"] += 1
                    processed_any = True
                    logger.debug(
                        "frame_processing_completed device_id=%s stream_id=%s sequence=%s "
                        "faces=%s events=%s queue_wait_ms=%.2f detect_ms=%.2f "
                        "association_ms=%.2f processing_ms=%.2f",
                        device_id,
                        stream_id,
                        sequence,
                        len(detections),
                        len(events),
                        queue_wait_ms,
                        detect_ms,
                        association_ms,
                        processing_ms,
                    )
                    if debug_detections is not None:
                        logger.info(
                            "frame_processed device_id=%s stream_id=%s sequence=%s faces=%d "
                            "queue_wait_ms=%.2f detect_ms=%.2f association_ms=%.2f processing_ms=%.2f",
                            device_id,
                            stream_id,
                            sequence,
                            len(debug_detections),
                            queue_wait_ms,
                            detect_ms,
                            association_ms,
                            processing_ms,
                        )
                        for face in debug_detections:
                            logger.info(
                                "face_detected device_id=%s stream_id=%s sequence=%s track_id=%s "
                                "bbox=%s detector_score=%.4f match_score=%s candidate_match=%s crop=%s",
                                device_id,
                                stream_id,
                                sequence,
                                face["track_id"],
                                face["bbox"],
                                face["detector_score"],
                                "n/a" if face["match_score"] is None else f"{face['match_score']:.4f}",
                                face["candidate_match"],
                                face.get("crop_id", "unavailable"),
                            )
                        await _report_debug_frame(
                            client,
                            {
                                "type": "debug_frame",
                                "device_id": device_id,
                                "stream_id": stream_id,
                                "sequence": sequence,
                                "captured_at": captured_at,
                                "queue_wait_ms": queue_wait_ms,
                                "detect_ms": detect_ms,
                                "association_ms": association_ms,
                                "processing_ms": processing_ms,
                                "faces": debug_detections,
                            },
                        )
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
    with _candidates_lock:
        candidates = list(_candidates.values())
    return {
        **_stats,
        "active_candidates": len(candidates),
        "recognition_ready_candidates": sum(
            bool(candidate.embeddings) for candidate in candidates
        ),
        "active_streams": len(_stream_queues),
        "face_engine_ready": _face_engine is not None,
    }
