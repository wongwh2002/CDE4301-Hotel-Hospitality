"""Device session and WebSocket connection manager for lounge-control.

Supports multiple paired phones concurrently connected to one lounge-control instance:
- Explicit token authentication from environment configuration
- Per-device and per-stream session tracking
- Safe disconnect cleanup
- Dispatches composed glanceable cues to the appropriate phone glasses bridge
"""

import hmac
import logging
import os
from typing import Any, Dict, Optional, Set
from fastapi import WebSocket
from contracts.models import is_valid_identifier

logger = logging.getLogger("device_manager")

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
    def __init__(self):
        # device_id -> WebSocket
        self._devices: Dict[str, WebSocket] = {}
        # device_id -> Set[stream_id]
        self._device_to_streams: Dict[str, Set[str]] = {}
        # stream_id -> device_id
        self._stream_to_device: Dict[str, str] = {}
        # device_id -> most recent frame_meta dict
        self._pending_meta: Dict[str, Dict[str, Any]] = {}

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
