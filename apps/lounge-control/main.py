"""FastAPI lounge-control service.

Orchestrates access events, active guest cohort, device WebSockets,
and cue delivery for the Hotel Smart-Glasses POC.
"""

import base64
import json
import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
import httpx
from pydantic import ValidationError
from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)

# Ensure local module directory and repo root are in path
MODULE_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODULE_DIR.parent.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from contracts.models import (
    CandidateEnrollment,
    CueMessage,
    CuePayload,
    DeviceStreamMessage,
    MatchEvent,
    TapEvent,
    utc_now_iso,
)
from cohort import ActiveCohortManager
from devices import (
    DeviceSessionManager,
    is_valid_identifier,
    verify_internal_token,
    verify_token,
)

logger = logging.getLogger("lounge_control")

MOCK_HOTEL_URL = os.environ.get("MOCK_HOTEL_URL", "http://mock-hotel:8002").rstrip("/")
FACE_WORKER_URL = os.environ.get("FACE_WORKER_URL", "http://face-worker:8001").rstrip("/")
COHORT_EXPIRY_SECONDS = int(os.environ.get("COHORT_EXPIRY_SECONDS", 7200))
INTERNAL_API_TOKEN = os.environ.get("INTERNAL_API_TOKEN", "")
MAX_FRAME_SIZE_BYTES = int(os.environ.get("MAX_FRAME_SIZE_BYTES", 5 * 1024 * 1024))

cohort_manager = ActiveCohortManager()
device_manager = DeviceSessionManager()
http_client: Optional[httpx.AsyncClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(timeout=10.0)
    yield
    if http_client:
        await http_client.aclose()


app = FastAPI(
    title="Lounge Control Service",
    description="Card tap ingestion, active cohort management, and device WebSocket hub",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint for Docker Compose."""
    return {
        "status": "ok",
        "service": "lounge-control",
        "cohort_size": cohort_manager.size(),
        "connected_devices": device_manager.connected_count(),
    }


@app.get("/v1/lounge/cohort", tags=["Lounge Operations"])
async def get_active_cohort():
    """Summary of active lounge cohort (non-sensitive fields only)."""
    return {
        "active_candidates": cohort_manager.get_summary(),
        "total_active": cohort_manager.size(),
    }


@app.post("/v1/lounge/taps", status_code=status.HTTP_200_OK, tags=["Lounge Operations"])
async def post_tap(event: TapEvent):
    """Handle card-reader tap events idempotently.

    - On entry: resolves guest profile from mock-hotel, enrolls candidate in
      face-worker, and places display fields in active cohort.
    - On exit: removes candidate from face-worker and clears active cohort.
    """
    # Check idempotency
    existing_outcome = cohort_manager.is_event_processed(event.event_id)
    if existing_outcome:
        return {
            "status": "acknowledged",
            "idempotent": True,
            **existing_outcome,
        }

    if event.event_type == "entry":
        # 1. Resolve minimal profile from mock-hotel
        assert http_client is not None
        try:
            profile_resp = await http_client.get(
                f"{MOCK_HOTEL_URL}/v1/guests/{event.guest_ref}/lounge-profile"
            )
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to connect to mock-hotel: {e}",
            )

        if profile_resp.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Guest reference '{event.guest_ref}' not found in hotel records",
            )
        profile_data = profile_resp.json()

        # 2. Fetch synthetic reference photo from mock-hotel
        try:
            photo_resp = await http_client.get(
                f"{MOCK_HOTEL_URL}/v1/guests/{event.guest_ref}/photo"
            )
            photo_bytes = photo_resp.content if photo_resp.status_code == 200 else b""
        except Exception:
            photo_bytes = b""

        # 3. Create opaque candidate ID (no PII in candidate_id)
        candidate_id = f"cand-{uuid.uuid4().hex[:12]}"
        expiry_dt = datetime.now(timezone.utc) + timedelta(seconds=COHORT_EXPIRY_SECONDS)
        expires_at = expiry_dt.isoformat()

        # 4. Enroll candidate in face-worker
        photo_b64 = base64.b64encode(photo_bytes).decode() if photo_bytes else None
        enrollment = CandidateEnrollment(
            candidate_id=candidate_id,
            expires_at=expires_at,
            photo_b64=photo_b64,
        )
        try:
            worker_resp = await http_client.put(
                f"{FACE_WORKER_URL}/internal/v1/candidates/{candidate_id}",
                json=enrollment.model_dump(),
                headers={"X-Internal-Token": INTERNAL_API_TOKEN},
            )
            if worker_resp.status_code not in (200, 201):
                logger.warning("Face worker returned status %s for enrollment", worker_resp.status_code)
        except Exception as e:
            logger.warning("Failed to enroll candidate into face-worker: %s", e)

        # 5. Store guest in active cohort (memory only)
        cohort_manager.admit_candidate(
            candidate_id=candidate_id,
            guest_ref=event.guest_ref,
            display_name=profile_data["display_name"],
            room_number=profile_data.get("room_number"),
            allergies=profile_data.get("allergies", []),
            preferences=profile_data.get("preferences", []),
            expires_at=expires_at,
        )

        outcome = {
            "action": "admitted",
            "candidate_id": candidate_id,
        }
        cohort_manager.record_event_processed(event.event_id, outcome)
        return outcome

    elif event.event_type == "exit":
        removed_candidates = cohort_manager.depart_guest(event.guest_ref)
        # Notify face-worker to remove each candidate template
        assert http_client is not None
        for cid in removed_candidates:
            try:
                await http_client.delete(
                    f"{FACE_WORKER_URL}/internal/v1/candidates/{cid}",
                    headers={"X-Internal-Token": INTERNAL_API_TOKEN},
                )
            except Exception as e:
                logger.warning("Failed to delete candidate %s from face-worker: %s", cid, e)

        outcome = {
            "action": "departed",
            "guest_ref": event.guest_ref,
            "removed_candidates": removed_candidates,
        }
        cohort_manager.record_event_processed(event.event_id, outcome)
        return outcome

    raise HTTPException(status_code=400, detail="Invalid event_type")


@app.post("/internal/v1/matches", status_code=status.HTTP_200_OK, tags=["Internal Matches"])
async def post_match(
    event: MatchEvent,
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
):
    """Receive internal face matching callback from face-worker.

    Composes glanceable cue and delivers to the connected phone WebSocket.
    """
    if not verify_internal_token(x_internal_token):
        raise HTTPException(status_code=401, detail="Invalid internal service token")

    if event.status != "stable_match":
        clear_message = CueMessage(
            type="clear",
            stream_id=event.stream_id,
            track_id=event.track_id,
            status="suppressed",
            cue=None,
            emitted_at=utc_now_iso(),
        )
        sent = await device_manager.send_cue(event.stream_id, clear_message.model_dump())
        return {
            "status": "suppressed" if sent else "device_not_connected",
            "stream_id": event.stream_id,
        }

    candidate = cohort_manager.get_candidate(event.candidate_id)
    if not candidate:
        logger.info("Match callback for non-active or expired candidate: %s", event.candidate_id)
        return {"status": "ignored", "reason": "candidate_not_active"}

    # Compose compact glanceable cue:
    # 🟢 ✅ ALEX
    # 🔴 ⚠️ PEANUT ALLERGY (if present)
    display_name = candidate["display_name"].upper()
    headline = f"🟢 ✅ {display_name}"

    alert = None
    secondary_color = None
    allergies = candidate.get("allergies", [])
    if allergies:
        alert = f"🔴 ⚠️ {allergies[0].upper()}"
        secondary_color = "red"

    cue_payload = CuePayload(
        headline=headline,
        alert=alert,
        color="green",
        secondary_color=secondary_color,
    )

    cue_message = CueMessage(
        type="cue",
        stream_id=event.stream_id,
        track_id=event.track_id,
        status="active",
        cue=cue_payload,
        emitted_at=utc_now_iso(),
    )

    sent = await device_manager.send_cue(event.stream_id, cue_message.model_dump(exclude_none=True))
    return {
        "status": "delivered" if sent else "device_not_connected",
        "stream_id": event.stream_id,
        "candidate_id": event.candidate_id,
    }


@app.websocket("/v1/devices/{device_id}/stream")
async def device_stream_endpoint(
    websocket: WebSocket,
    device_id: str,
    token: Optional[str] = Query(None),
):
    """Authenticated WebSocket for paired phone companion app / frame replay.

    - Authenticates explicitly via query parameter or Authorization header
    - Accepts frame metadata and binary JPEG frames
    - Forwards transient frames via internal HTTP to face-worker
    - Pushes glanceable cue messages to connected companion device
    - Cleans up session and stream state upon disconnect
    """
    # Check authentication
    auth_header = websocket.headers.get("authorization", "")
    bearer_token = None
    if auth_header.lower().startswith("bearer "):
        bearer_token = auth_header[7:].strip()

    candidate_token = token or bearer_token

    if not is_valid_identifier(device_id) or not verify_token(candidate_token):
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Unauthorized: valid device ID and token required",
        )
        return

    await websocket.accept()
    if not device_manager.register(device_id, websocket):
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="A session for this device is already connected",
        )
        return

    try:
        await websocket.send_json({"type": "session_ack", "status": "authenticated", "device_id": device_id})
        while True:
            message = await websocket.receive()
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    device_message = DeviceStreamMessage.model_validate(data)
                except (json.JSONDecodeError, ValidationError, TypeError):
                    await websocket.send_json({"type": "error", "message": "Invalid device message"})
                    continue

                if device_message.device_id and device_message.device_id != device_id:
                    await websocket.send_json({"type": "error", "message": "device_id does not match session"})
                    continue

                if device_message.type == "frame_meta":
                    if not device_manager.set_pending_meta(
                        device_id,
                        device_message.model_dump(exclude_none=True),
                    ):
                        await websocket.send_json({"type": "error", "message": "stream_id is already in use"})
                        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                        break
                elif device_message.type == "frame" and device_message.payload_b64:
                    try:
                        frame_bytes = base64.b64decode(device_message.payload_b64, validate=True)
                    except ValueError:
                        await websocket.send_json({"type": "error", "message": "Invalid frame encoding"})
                        continue
                    if len(frame_bytes) > MAX_FRAME_SIZE_BYTES:
                        await websocket.close(code=1009, reason="Frame exceeds maximum size")
                        break
                    if not device_manager.bind_stream(device_id, device_message.stream_id):
                        await websocket.send_json({"type": "error", "message": "stream_id is already in use"})
                        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                        break
                    await forward_frame_to_worker(
                        device_id=device_id,
                        stream_id=device_message.stream_id,
                        sequence=device_message.sequence,
                        captured_at=device_message.captured_at or utc_now_iso(),
                        frame_bytes=frame_bytes,
                    )
                    del frame_bytes
                elif device_message.type == "ping":
                    await websocket.send_json({"type": "pong"})
                else:
                    await websocket.send_json({"type": "error", "message": "Unsupported device message"})

            elif "bytes" in message:
                # Raw binary JPEG frame preceded by frame_meta
                frame_bytes = message["bytes"]
                meta = device_manager.get_and_clear_pending_meta(device_id)
                if not meta:
                    await websocket.send_json({"type": "error", "message": "Send frame_meta before binary frame"})
                    continue
                if len(frame_bytes) > MAX_FRAME_SIZE_BYTES:
                    await websocket.close(code=1009, reason="Frame exceeds maximum size")
                    break

                await forward_frame_to_worker(
                    device_id=device_id,
                    stream_id=meta["stream_id"],
                    sequence=meta["sequence"],
                    captured_at=meta["captured_at"],
                    frame_bytes=frame_bytes,
                )
                del frame_bytes

    except WebSocketDisconnect:
        logger.info("Device disconnected: %s", device_id)
    except Exception as e:
        logger.error("Error in device stream %s: %s", device_id, e)
    finally:
        device_manager.unregister(device_id, websocket)


async def forward_frame_to_worker(
    device_id: str,
    stream_id: str,
    sequence: int,
    captured_at: str,
    frame_bytes: bytes,
) -> None:
    """Forward transient frame to face-worker via internal HTTP.

    Never logs or persists the frame payload.
    """
    if not http_client:
        return

    if len(frame_bytes) > MAX_FRAME_SIZE_BYTES:
        logger.warning("Rejected oversized device frame (%d bytes)", len(frame_bytes))
        return

    headers = {
        "Content-Type": "image/jpeg",
        "X-Device-Id": device_id,
        "X-Stream-Id": stream_id,
        "X-Sequence": str(sequence),
        "X-Captured-At": captured_at,
        "X-Internal-Token": INTERNAL_API_TOKEN,
    }

    try:
        resp = await http_client.post(
            f"{FACE_WORKER_URL}/internal/v1/frames",
            content=frame_bytes,
            headers=headers,
        )
        if resp.status_code not in (200, 202):
            logger.warning("Face worker returned status %s for frame handoff", resp.status_code)
    except Exception as e:
        logger.warning("Failed to forward frame to face-worker: %s", e)
