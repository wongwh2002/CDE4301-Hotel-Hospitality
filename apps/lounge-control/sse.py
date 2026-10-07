"""Server-Sent Events notifier for active lounge roster changes.

Provides bounded per-client event queues and keepalive frames to
ensure reliable, real-time dashboard updates without memory leaks.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, Set

logger = logging.getLogger("lounge_control.sse")


class RosterSSENotifier:
    """Manages SSE subscriptions with bounded per-client buffering."""

    def __init__(self, max_buffer_size: int = 16):
        self._subscribers: Set[asyncio.Queue] = set()
        self._max_buffer_size = max_buffer_size

    def subscribe(self) -> asyncio.Queue:
        """Register a new SSE client subscriber with a bounded queue."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=self._max_buffer_size)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        """Remove a subscriber queue upon client disconnect."""
        self._subscribers.discard(queue)

    def subscriber_count(self) -> int:
        """Return number of currently active SSE subscriptions."""
        return len(self._subscribers)

    def notify(
        self,
        event_type: str = "roster_change",
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Broadcast an event to all subscribers.

        Drops the oldest unconsumed item if a subscriber queue is full,
        guaranteeing bounded buffering per client.
        """
        payload = {
            "event": event_type,
            "data": data or {},
        }
        for q in list(self._subscribers):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                try:
                    q.put_nowait(payload)
                except asyncio.QueueFull:
                    logger.warning("Dropped SSE event due to queue saturation")


def format_sse(event_type: str, data: Any) -> str:
    """Format a message in the SSE wire protocol."""
    payload_str = json.dumps(data) if not isinstance(data, str) else data
    return f"event: {event_type}\ndata: {payload_str}\n\n"


def format_keepalive() -> str:
    """Format an SSE comment keepalive frame."""
    return ": keepalive\n\n"
