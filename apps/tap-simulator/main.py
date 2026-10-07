"""Tap event simulator for Hotel Smart-Glasses POC.

Sends simulated entry and exit card-reader tap events to lounge-control
using the standard tap-event contract and synthetic guest references.
"""

import argparse
import asyncio
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List
import httpx

# Ensure local module directory and repo root are in path
MODULE_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODULE_DIR.parent.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from contracts.models import TapEvent, utc_now_iso

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("tap_simulator")

DEFAULT_TARGET_URL = os.environ.get("TARGET_URL", "http://lounge-control:8000/v1/lounge/taps")
DEFAULT_READER_ID = os.environ.get("READER_ID", "lounge-entry-1")
DEFAULT_GUESTS = os.environ.get("GUEST_REFS", "guest-alex-101,guest-jordan-102,guest-casey-103,guest-samira-104").split(",")
DEFAULT_INTERVAL = float(os.environ.get("INTERVAL_SECONDS", "5"))
DEFAULT_MODE = os.environ.get("MODE", "loop")


async def send_tap_event(
    client: httpx.AsyncClient,
    target_url: str,
    reader_id: str,
    guest_ref: str,
    event_type: str,
) -> bool:
    """Send a single tap event to lounge-control."""
    event = TapEvent(
        event_id=f"evt-{uuid.uuid4().hex[:10]}",
        reader_id=reader_id,
        guest_ref=guest_ref.strip(),
        event_type=event_type,
        occurred_at=utc_now_iso(),
    )
    logger.info("Sending %s tap for %s (event_id=%s)", event_type, guest_ref, event.event_id)
    try:
        resp = await client.post(target_url, json=event.model_dump())
        if resp.status_code == 200:
            logger.info("Tap accepted: %s", resp.json())
            return True
        else:
            logger.error("Tap rejected with status %d: %s", resp.status_code, resp.text)
            return False
    except Exception as e:
        logger.error("Failed to connect to lounge-control at %s: %s", target_url, e)
        return False


async def run_simulation(
    target_url: str,
    reader_id: str,
    guest_refs: List[str],
    interval: float,
    mode: str,
):
    """Run tap simulation in once or loop mode."""
    logger.info("Starting tap simulator (target=%s, mode=%s, interval=%.1fs)", target_url, mode, interval)
    async with httpx.AsyncClient(timeout=10.0) as client:
        active_in_lounge = set()
        guest_index = 0

        while True:
            guest_ref = guest_refs[guest_index % len(guest_refs)].strip()
            # Toggle entry/exit
            if guest_ref in active_in_lounge:
                event_type = "exit"
                active_in_lounge.remove(guest_ref)
            else:
                event_type = "entry"
                active_in_lounge.add(guest_ref)

            await send_tap_event(
                client=client,
                target_url=target_url,
                reader_id=reader_id,
                guest_ref=guest_ref,
                event_type=event_type,
            )

            guest_index += 1

            if mode == "once" and guest_index >= len(guest_refs):
                logger.info("Completed once mode tap sequence")
                break

            await asyncio.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Simulate card-reader taps for Hotel POC")
    parser.add_argument("--url", default=DEFAULT_TARGET_URL, help="Target lounge-control taps URL")
    parser.add_argument("--reader", default=DEFAULT_READER_ID, help="Reader ID")
    parser.add_argument("--guests", default=",".join(DEFAULT_GUESTS), help="Comma-separated guest refs")
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL, help="Interval between taps (s)")
    parser.add_argument("--mode", choices=["loop", "once"], default=DEFAULT_MODE, help="Run mode")

    args = parser.parse_args()
    guests = [g.strip() for g in args.guests.split(",") if g.strip()]

    try:
        asyncio.run(run_simulation(
            target_url=args.url,
            reader_id=args.reader,
            guest_refs=guests,
            interval=args.interval,
            mode=args.mode,
        ))
    except KeyboardInterrupt:
        logger.info("Tap simulator stopped by user")


if __name__ == "__main__":
    main()
