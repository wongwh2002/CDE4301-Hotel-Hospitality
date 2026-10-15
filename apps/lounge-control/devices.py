"""Device session and WebSocket connection manager for lounge-control.

Supports multiple paired phones concurrently connected to one lounge-control instance:
- Explicit token authentication from environment configuration
- Per-device and per-stream session tracking
- Safe disconnect cleanup
- Dispatches cues, transient crops, and detection snapshots to the phone glasses bridge
"""

import hmac
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set
from fastapi import WebSocket
from contracts.models import is_valid_identifier

logger = logging.getLogger("device_manager")
DETECTION_TTL_SECONDS = float(os.environ.get("DETECTION_TTL_SECONDS", "5"))

def verify_token(provided_token: Optional[str]) -> bool:
    """Verify device authentication token against environment configuration."""
    expected = os.environ.get("DEVICE_AUTH_TOKEN", "").strip()
    if not expected or not provided_token:
        return False
    return hmac.compare_digest(provided_token.strip(), expected)


def verify_internal_token(provided_token: Optional[str]) -> bool:
    """Verify service-to-service requests using a separate configured token."""
    expected = os.environ.get("INTERNAL_API_TOKEN", "").strip()
    if not expected or not provided_token:
        return False
    return hmac.compare_digest(provided_token.strip(), expected)


class DeviceSessionManager:
    def __init__(self, detection_ttl_seconds: float = DETECTION_TTL_SECONDS):
        # device_id -> WebSocket
        self._devices: Dict[str, WebSocket] = {}
        # device_id -> Set[stream_id]
        self._device_to_streams: Dict[str, Set[str]] = {}
        # stream_id -> device_id
        self._stream_to_device: Dict[str, str] = {}
        # device_id -> most recent frame_meta dict
        self._pending_meta: Dict[str, Dict[str, Any]] = {}
        # stream_id -> track_id -> person metadata and last stable observation
        self._detected_people: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._detection_ttl_seconds = detection_ttl_seconds
        self.detection_ttl_seconds = detection_ttl_seconds

    def register(self, device_id: str, websocket: WebSocket) -> bool:
        """Register an authenticated device connection unless one is active."""
        if device_id in self._devices:
            return False
        self._devices[device_id] = websocket
        if device_id not in self._device_to_streams:
            self._device_to_streams[device_id] = set()
        logger.info("Registered device session: %s", device_id)
        return True

    def unregister(self, device_id: str, websocket: Optional[WebSocket] = None) -> None:
        """Clean up sessions and stream mappings on disconnect."""
        if websocket is not None and self._devices.get(device_id) is not websocket:
            return
        self._devices.pop(device_id, None)
        self._pending_meta.pop(device_id, None)
        stream_ids = self._device_to_streams.pop(device_id, set())
        for sid in stream_ids:
            self._stream_to_device.pop(sid, None)
            self._detected_people.pop(sid, None)
        logger.info("Cleaned up device session: %s (cleared %d streams)", device_id, len(stream_ids))

    def bind_stream(self, device_id: str, stream_id: str) -> bool:
        """Associate a camera stream with a device."""
        if device_id not in self._device_to_streams:
            return False
        owner = self._stream_to_device.get(stream_id)
        if owner is not None and owner != device_id:
            return False
        self._device_to_streams[device_id].add(stream_id)
        self._stream_to_device[stream_id] = device_id
        return True

    def has_stream(self, stream_id: str) -> bool:
        """Return whether a stream is already bound to an authenticated device."""
        return stream_id in self._stream_to_device

    def set_pending_meta(self, device_id: str, meta: Dict[str, Any]) -> bool:
        """Store stream metadata preceding a binary JPEG frame."""
        stream_id = meta.get("stream_id")
        if not stream_id or not self.bind_stream(device_id, stream_id):
            return False
        self._pending_meta[device_id] = meta
        return True

    def get_and_clear_pending_meta(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve and clear pending metadata for an incoming binary frame."""
        return self._pending_meta.pop(device_id, None)

    def update_detected_person(
        self,
        stream_id: str,
        track_id: str,
        person: Optional[Dict[str, Any]],
        now: Optional[float] = None,
        last_seen: Optional[float] = None,
    ) -> list[Dict[str, Any]]:
        """Update one stable track and return the full current set for its stream."""
        if stream_id not in self._stream_to_device:
            return []
        stream_people = self._detected_people.setdefault(stream_id, {})
        if person is None:
            stream_people.pop(track_id, None)
        else:
            current_time = time.monotonic() if now is None else now
            stream_people[track_id] = {
                "person": {"track_id": track_id, **person},
                "last_seen": current_time if last_seen is None else last_seen,
            }
        return self.get_detected_people(stream_id, now=now)

    def observation_last_seen(
        self,
        observed_at: datetime,
        now_monotonic: Optional[float] = None,
        now_utc: Optional[datetime] = None,
    ) -> Optional[float]:
        """Convert a fresh UTC observation time to monotonic time for TTL expiry."""
        current_utc = datetime.now(timezone.utc) if now_utc is None else now_utc
        current_monotonic = time.monotonic() if now_monotonic is None else now_monotonic
        age_seconds = max(0.0, (current_utc - observed_at).total_seconds())
        if age_seconds >= self._detection_ttl_seconds:
            return None
        return current_monotonic - age_seconds

    def get_detected_people(
        self, stream_id: str, now: Optional[float] = None
    ) -> list[Dict[str, Any]]:
        """Return a copy of unexpired matches, dropping stale track metadata."""
        stream_people = self._detected_people.get(stream_id)
        if not stream_people:
            return []
        current_time = time.monotonic() if now is None else now
        expired = [
            track_id
            for track_id, entry in stream_people.items()
            if current_time - entry["last_seen"] >= self._detection_ttl_seconds
        ]
        for track_id in expired:
            stream_people.pop(track_id, None)
        if not stream_people:
            self._detected_people.pop(stream_id, None)
            return []
        return [dict(entry["person"]) for entry in stream_people.values()]

    def get_detected_person(
        self, stream_id: str, track_id: str, now: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Return one unexpired track entry, if present."""
        self.get_detected_people(stream_id, now=now)
        entry = self._detected_people.get(stream_id, {}).get(track_id)
        return dict(entry["person"]) if entry else None

    def stream_ids(self) -> tuple[str, ...]:
        """Return currently connected camera stream identifiers."""
        return tuple(self._stream_to_device)

    def remove_guest(self, guest_id: str) -> Dict[str, list[str]]:
        """Remove a guest's visible tracks and return them grouped by stream."""
        removed: Dict[str, list[str]] = {}
        for stream_id, stream_people in list(self._detected_people.items()):
            track_ids = [
                track_id
                for track_id, entry in stream_people.items()
                if entry["person"].get("guest_id") == guest_id
            ]
            if track_ids:
                removed[stream_id] = track_ids
                for track_id in track_ids:
                    stream_people.pop(track_id, None)
                if not stream_people:
                    self._detected_people.pop(stream_id, None)
        return removed

    async def send_cue(self, stream_id: str, cue_payload: Dict[str, Any]) -> bool:
        """Send glanceable cue to the companion phone owning this stream."""
        device_id = self._stream_to_device.get(stream_id)
        if not device_id:
            logger.warning("No device registered for stream_id: %s", stream_id)
            return False

        ws = self._devices.get(device_id)
        if not ws:
            logger.warning("Device %s WebSocket connection not active", device_id)
            return False

        try:
            await ws.send_json(cue_payload)
            return True
        except Exception as e:
            logger.error("Failed to send cue to device %s: %s", device_id, e)
            return False

    def connected_count(self) -> int:
        return len(self._devices)
