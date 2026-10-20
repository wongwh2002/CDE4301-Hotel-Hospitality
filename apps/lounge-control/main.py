"""FastAPI lounge-control service.

Orchestrates access events, active guest cohort, device WebSockets,
and cue delivery for the Hotel Smart-Glasses POC.
"""

import asyncio
import base64
import hashlib
import hmac
from html import escape as escape_html
import json
import logging
import os
import re
import sys
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional
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
from fastapi.responses import HTMLResponse, Response, StreamingResponse

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
    DetectionSetMessage,
    DebugFrameMessage,
    DeviceStreamMessage,
    FaceCropMessage,
    GuestRegistrationRequest,
    GuestUpdateRequest,
    LoungeProfile,
    MatchEvent,
    TapEvent,
    utc_now_iso,
)
from cohort import ActiveCohortManager
from dashboard import DASHBOARD_HTML
from devices import (
    DeviceSessionManager,
    is_valid_identifier,
    verify_internal_token,
    verify_token,
)
from sse import RosterSSENotifier, format_keepalive, format_sse

# Uvicorn configures its own loggers, but this service also needs application
# INFO records (for example, frame receipt) to reach the container log stream.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lounge_control")
# Uvicorn's default setup may leave application loggers inheriting WARNING.
# Keep POC operational logs, including per-frame INFO messages, visible in Compose.
logger.setLevel(logging.INFO)

MOCK_HOTEL_URL = os.environ.get("MOCK_HOTEL_URL", "http://mock-hotel:8002").rstrip("/")
FACE_WORKER_URL = os.environ.get("FACE_WORKER_URL", "http://face-worker:8001").rstrip("/")
COHORT_EXPIRY_SECONDS = int(os.environ.get("COHORT_EXPIRY_SECONDS", 7200))
INTERNAL_API_TOKEN = os.environ.get("INTERNAL_API_TOKEN", "")
MAX_FRAME_SIZE_BYTES = int(os.environ.get("MAX_FRAME_SIZE_BYTES", 5 * 1024 * 1024))
DETECTION_SET_INTERVAL_SECONDS = float(os.environ.get("DETECTION_SET_INTERVAL_SECONDS", "1"))
CANDIDATE_RECONCILE_INTERVAL_SECONDS = float(
    os.environ.get("CANDIDATE_RECONCILE_INTERVAL_SECONDS", "5")
)
TERMINAL_RECOGNITION_STATUSES = {
    "no_reference_photos",
    "no_single_face",
    "recognition_disabled",
    "enrollment_failed",
}

cohort_manager = ActiveCohortManager()
device_manager = DeviceSessionManager()
sse_notifier = RosterSSENotifier()
tap_locks: Dict[str, asyncio.Lock] = {}
http_client: Optional[httpx.AsyncClient] = None


def public_guest_id(guest_ref: str) -> str:
    """Return a stable opaque guest ID without exposing the hotel reference."""
    key = (INTERNAL_API_TOKEN or "hotel-lounge-poc").encode("utf-8")
    digest = hmac.new(key, guest_ref.encode("utf-8"), hashlib.sha256).hexdigest()[:24]
    return f"guest-{digest}"


async def publish_detection_set(stream_id: str) -> bool:
    """Send the current unexpired set of identified tracks to their phone."""
    message = DetectionSetMessage(
        type="detection_set",
        stream_id=stream_id,
        people=device_manager.get_detected_people(stream_id),
    )
    return await device_manager.send_cue(
        stream_id,
        message.model_dump(exclude_none=True),
    )


async def detection_set_broadcast_loop() -> None:
    """Refresh full snapshots once per second for every active device stream."""
    while True:
        try:
            await asyncio.sleep(DETECTION_SET_INTERVAL_SECONDS)
            for stream_id in device_manager.stream_ids():
                await publish_detection_set(stream_id)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Failed to publish a periodic detection set")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(timeout=10.0)
    detection_task = asyncio.create_task(detection_set_broadcast_loop())
    reconciliation_task = asyncio.create_task(candidate_reconciliation_loop())
    try:
        yield
    finally:
        detection_task.cancel()
        reconciliation_task.cancel()
        try:
            await detection_task
        except asyncio.CancelledError:
            pass
        try:
            await reconciliation_task
        except asyncio.CancelledError:
            pass
        if http_client:
            await http_client.aclose()


app = FastAPI(
    title="Lounge Control Service",
    description="Card tap ingestion, active cohort management, and device WebSocket hub",
    version="0.1.0",
    lifespan=lifespan,
)


ALLERGY_EMOJI_RULES = (
    (("peanut", "peanuts", "groundnut", "groundnuts"), "🥜"),
    (("shrimp", "shrimps", "prawn", "prawns"), "🦐"),
    (("crab", "crabs"), "🦀"),
    (("lobster", "lobsters"), "🦞"),
    (("fish",), "🐟"),
    (("milk", "dairy"), "🥛"),
    (("egg", "eggs"), "🥚"),
    (("wheat",), "🌾"),
)


def allergy_emoji(allergy_text: str) -> str:
    """Return a familiar emoji for a known allergen, if there is a clear one."""
    words = set(re.findall(r"[a-z]+", allergy_text.lower()))
    for terms, emoji in ALLERGY_EMOJI_RULES:
        if words.intersection(terms):
            return emoji
    return ""


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint for Docker Compose."""
    return {
        "status": "ok",
        "service": "lounge-control",
        "cohort_size": cohort_manager.size(),
        "recognition_pending_candidates": cohort_manager.pending_recognition_count(),
        "connected_devices": device_manager.connected_count(),
    }


@app.get("/v1/lounge/cohort", tags=["Lounge Operations"])
async def get_active_cohort():
    """Summary of active lounge cohort (non-sensitive fields only)."""
    return {
        "active_candidates": cohort_manager.get_summary(),
        "total_active": cohort_manager.size(),
    }


@app.get("/v1/lounge/roster", tags=["Lounge Operations"])
async def get_active_roster():
    """Summary of active lounge roster (display_name and admitted_at only)."""
    return cohort_manager.get_roster()


@app.get("/v1/lounge/events", tags=["Lounge Operations"])
@app.get("/v1/lounge/sse", tags=["Lounge Operations"])
async def sse_roster_events(request: Request):
    """Server-Sent Events signaling active roster changes with keepalives."""
    q = sse_notifier.subscribe()

    async def event_generator():
        try:
            yield format_sse("connected", {"status": "ok"})
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield format_sse(msg["event"], msg["data"])
                except asyncio.TimeoutError:
                    yield format_keepalive()
        except asyncio.CancelledError:
            pass
        finally:
            sse_notifier.unsubscribe(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
async def get_dashboard():
    """Laptop dashboard for staff access control and active roster."""
    device_token = escape_html(
        os.environ.get("DEVICE_AUTH_TOKEN", "gedi-4301"),
        quote=True,
    )
    dashboard_html = DASHBOARD_HTML.replace("__DEVICE_AUTH_TOKEN__", device_token)
    return HTMLResponse(content=dashboard_html, media_type="text/html")


@app.get("/v1/dashboard/guests", tags=["Dashboard"])
@app.get("/v1/lounge/guests", tags=["Dashboard"])
async def list_hotel_guests_for_dashboard():
    """List registered hotel guests for staff dashboard dropdown."""
    if not http_client:
        return []
    try:
        resp = await http_client.get(f"{MOCK_HOTEL_URL}/v1/guests")
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception as e:
        logger.warning("Failed to fetch hotel guests from mock-hotel: %s", e)
        return []


@app.get("/v1/dashboard/guests/{guest_ref}/photos/{photo_index}", tags=["Dashboard"])
async def get_dashboard_guest_photo(guest_ref: str, photo_index: int):
    """Serve an existing guest reference JPEG through the dashboard's origin."""
    if photo_index < 0 or photo_index > 2:
        raise HTTPException(status_code=404, detail="Reference photo not found")
    if not http_client:
        raise HTTPException(status_code=503, detail="mock-hotel client is unavailable")
    try:
        resp = await http_client.get(
            f"{MOCK_HOTEL_URL}/v1/guests/{guest_ref}/photos/{photo_index}"
        )
    except Exception as exc:
        logger.warning("Failed to fetch guest reference photo from mock-hotel: %s", exc)
        raise HTTPException(status_code=502, detail="Failed to connect to mock-hotel") from exc
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail="Reference photo not found")
    return Response(content=resp.content, media_type="image/jpeg")


@app.post(
    "/v1/dashboard/guests",
    response_model=LoungeProfile,
    status_code=status.HTTP_201_CREATED,
    tags=["Dashboard"],
)
async def register_dashboard_guest(request: GuestRegistrationRequest):
    """Register a mock hotel guest through the same-origin dashboard API."""
    if not http_client:
        raise HTTPException(status_code=503, detail="mock-hotel client is unavailable")
    try:
        resp = await http_client.post(
            f"{MOCK_HOTEL_URL}/v1/guests",
            json=request.model_dump(),
        )
    except Exception as e:
        logger.warning("Failed to register guest through mock-hotel: %s", e)
        raise HTTPException(status_code=502, detail="Failed to connect to mock-hotel")

    try:
        result = resp.json()
    except ValueError:
        result = {}
    if resp.status_code >= 400:
        error_detail = result.get("detail", "mock-hotel guest registration failed")
        status_code = resp.status_code if resp.status_code < 500 else 502
        raise HTTPException(status_code=status_code, detail=error_detail)
    return result


@app.patch(
    "/v1/dashboard/guests/{guest_ref}",
    response_model=LoungeProfile,
    tags=["Dashboard"],
)
async def update_dashboard_guest(guest_ref: str, request: GuestUpdateRequest):
    """Edit a mock guest through the same-origin dashboard API."""
    if not http_client:
        raise HTTPException(status_code=503, detail="mock-hotel client is unavailable")
    try:
        resp = await http_client.patch(
            f"{MOCK_HOTEL_URL}/v1/guests/{guest_ref}",
            json=request.model_dump(exclude_unset=True),
        )
    except Exception as e:
        logger.warning("Failed to update guest through mock-hotel: %s", e)
        raise HTTPException(status_code=502, detail="Failed to connect to mock-hotel")

    try:
        result = resp.json()
    except ValueError:
        result = {}
    if resp.status_code >= 400:
        error_detail = result.get("detail", "mock-hotel guest update failed")
        status_code = resp.status_code if resp.status_code < 500 else 502
        raise HTTPException(status_code=status_code, detail=error_detail)
    return result


async def _enroll_candidate_with_worker(
    candidate_id: str,
    guest_ref: str,
    expires_at: str,
    profile_data: Optional[dict] = None,
) -> str:
    """Enroll or re-enroll an active guest; return readiness or retry state."""
    if http_client is None:
        return "enrollment_pending"

    if profile_data is None:
        try:
            profile_resp = await http_client.get(
                f"{MOCK_HOTEL_URL}/v1/guests/{guest_ref}/lounge-profile"
            )
        except Exception:
            logger.warning(
                "candidate_enrollment_deferred candidate_id=%s dependency=mock_hotel_profile",
                candidate_id,
            )
            return "enrollment_pending"
        if profile_resp.status_code == 404:
            logger.warning(
                "candidate_enrollment_failed candidate_id=%s reason=guest_profile_missing",
                candidate_id,
            )
            return "enrollment_failed"
        if profile_resp.status_code >= 500:
            logger.warning(
                "candidate_enrollment_deferred candidate_id=%s dependency=mock_hotel_profile status=%s",
                candidate_id,
                profile_resp.status_code,
            )
            return "enrollment_pending"
        if profile_resp.status_code != 200:
            return "enrollment_failed"
        try:
            profile_data = profile_resp.json()
        except ValueError:
            logger.warning(
                "candidate_enrollment_deferred candidate_id=%s reason=invalid_profile_response",
                candidate_id,
            )
            return "enrollment_pending"
        if not isinstance(profile_data, dict):
            logger.warning(
                "candidate_enrollment_deferred candidate_id=%s reason=invalid_profile_response",
                candidate_id,
            )
            return "enrollment_pending"

    photo_urls = profile_data.get("photo_urls") or [
        profile_data.get("photo_url") or f"/v1/guests/{guest_ref}/photo"
    ]
    photos_b64: list[str] = []
    for photo_url in photo_urls[:3]:
        try:
            photo_resp = await http_client.get(f"{MOCK_HOTEL_URL}{photo_url}")
        except Exception:
            logger.warning(
                "candidate_enrollment_deferred candidate_id=%s dependency=mock_hotel_photo",
                candidate_id,
            )
            return "enrollment_pending"
        if photo_resp.status_code == 404:
            continue
        if photo_resp.status_code >= 500:
            logger.warning(
                "candidate_enrollment_deferred candidate_id=%s dependency=mock_hotel_photo status=%s",
                candidate_id,
                photo_resp.status_code,
            )
            return "enrollment_pending"
        if photo_resp.status_code != 200:
            logger.warning(
                "candidate_enrollment_failed candidate_id=%s reason=reference_photo status=%s",
                candidate_id,
                photo_resp.status_code,
            )
            return "enrollment_failed"
        if photo_resp.content:
            photos_b64.append(base64.b64encode(photo_resp.content).decode("ascii"))

    enrollment = CandidateEnrollment(
        candidate_id=candidate_id,
        expires_at=expires_at,
        photos_b64=photos_b64,
    )
    try:
        worker_resp = await http_client.put(
            f"{FACE_WORKER_URL}/internal/v1/candidates/{candidate_id}",
            json=enrollment.model_dump(),
            headers={"X-Internal-Token": INTERNAL_API_TOKEN},
        )
    except Exception:
        logger.warning(
            "candidate_enrollment_deferred candidate_id=%s dependency=face_worker",
            candidate_id,
        )
        return "enrollment_pending"

    if worker_resp.status_code >= 500:
        logger.warning(
            "candidate_enrollment_deferred candidate_id=%s dependency=face_worker status=%s",
            candidate_id,
            worker_resp.status_code,
        )
        return "enrollment_pending"
    if worker_resp.status_code not in (200, 201):
        logger.warning(
            "candidate_enrollment_failed candidate_id=%s dependency=face_worker status=%s",
            candidate_id,
            worker_resp.status_code,
        )
        return "enrollment_failed"

    try:
        worker_result = worker_resp.json()
    except ValueError:
        logger.warning(
            "candidate_enrollment_deferred candidate_id=%s reason=invalid_worker_response",
            candidate_id,
        )
        return "enrollment_pending"
    template_status = (
        worker_result.get("template_status") if isinstance(worker_result, dict) else None
    )
    if not isinstance(template_status, str) or not template_status:
        return "enrollment_pending"
    logger.info(
        "candidate_enrollment_status candidate_id=%s template_status=%s reference_photos=%s",
        candidate_id,
        template_status,
        len(photos_b64),
    )
    return template_status


async def reconcile_candidate_templates() -> None:
    """Restore active candidate templates after an enrollment failure or worker restart."""
    if http_client is None:
        return
    try:
        response = await http_client.get(
            f"{FACE_WORKER_URL}/internal/v1/candidates",
            headers={"X-Internal-Token": INTERNAL_API_TOKEN},
        )
        if response.status_code != 200:
            logger.warning("candidate_reconciliation_unavailable worker_status=%s", response.status_code)
            return
        worker_candidate_ids = set(response.json())
    except Exception:
        logger.warning("candidate_reconciliation_unavailable dependency=face_worker")
        return

    for candidate in cohort_manager.get_candidates():
        candidate_id = candidate["candidate_id"]
        recognition_status = candidate.get("recognition_status", "enrollment_pending")
        if candidate_id in worker_candidate_ids:
            if recognition_status == "enrollment_pending":
                try:
                    status_resp = await http_client.get(
                        f"{FACE_WORKER_URL}/internal/v1/candidates/{candidate_id}",
                        headers={"X-Internal-Token": INTERNAL_API_TOKEN},
                    )
                    if status_resp.status_code == 200:
                        template_status = status_resp.json().get("template_status")
                        if isinstance(template_status, str):
                            cohort_manager.set_recognition_status(candidate_id, template_status)
                except Exception:
                    logger.debug("candidate_status_lookup_failed candidate_id=%s", candidate_id)
            continue

        # Empty or invalid reference sets are not transient. A worker restart
        # does not make them recoverable; new photos require re-enrollment.
        if recognition_status in TERMINAL_RECOGNITION_STATUSES:
            continue

        restored_status = await _enroll_candidate_with_worker(
            candidate_id=candidate_id,
            guest_ref=candidate["guest_ref"],
            expires_at=candidate["expires_at"],
        )
        previous_status = recognition_status
        cohort_manager.set_recognition_status(candidate_id, restored_status)
        if restored_status != previous_status:
            logger.info(
                "candidate_reconciliation_updated candidate_id=%s previous_status=%s status=%s",
                candidate_id,
                previous_status,
                restored_status,
            )


async def candidate_reconciliation_loop() -> None:
    """Periodically retry pending enrollment and recover templates after worker restarts."""
    while True:
        try:
            await asyncio.sleep(CANDIDATE_RECONCILE_INTERVAL_SECONDS)
            await reconcile_candidate_templates()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Candidate enrollment reconciliation failed")


@app.post("/v1/lounge/taps", status_code=status.HTTP_200_OK, tags=["Lounge Operations"])
async def post_tap(event: TapEvent):
    """Serialize taps for each guest while allowing different guests in parallel."""
    lock = tap_locks.setdefault(event.guest_ref, asyncio.Lock())
    async with lock:
        return await _process_tap(event)


async def _process_tap(event: TapEvent):
    """Handle card-reader tap events idempotently.

    - On entry: enforces at most one active presence per guest_ref,
      resolves guest profile, enrolls candidate in face-worker, places display
      fields in active cohort, and notifies SSE listeners on roster change.
    - On exit: removes active presence from face-worker and cohort,
      and notifies SSE listeners on roster change.
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
        # Enforce at most one active presence per guest_ref, even across new event_ids
        existing_candidate_id = cohort_manager.get_candidate_for_guest(event.guest_ref)
        if existing_candidate_id:
            existing_candidate = cohort_manager.get_candidate(existing_candidate_id) or {}
            recognition_status = existing_candidate.get(
                "recognition_status", "enrollment_pending"
            )
            if recognition_status == "enrollment_pending":
                recognition_status = await _enroll_candidate_with_worker(
                    candidate_id=existing_candidate_id,
                    guest_ref=event.guest_ref,
                    expires_at=existing_candidate.get("expires_at", utc_now_iso()),
                )
                cohort_manager.set_recognition_status(
                    existing_candidate_id, recognition_status
                )
            outcome = {
                "action": "already_admitted",
                "candidate_id": existing_candidate_id,
                "recognition_status": recognition_status,
                "status": "acknowledged",
            }
            cohort_manager.record_event_processed(event.event_id, outcome)
            return outcome

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

        # 2. Create opaque candidate ID (no PII in candidate_id)
        candidate_id = f"cand-{uuid.uuid4().hex[:12]}"
        expiry_dt = datetime.now(timezone.utc) + timedelta(seconds=COHORT_EXPIRY_SECONDS)
        expires_at = expiry_dt.isoformat()

        # 3. Record lounge presence first. Enrollment runs off face-worker's
        # event loop; failures stay visibly pending and are retried by the
        # reconciliation task instead of silently becoming unmatchable.
        cohort_manager.admit_candidate(
            candidate_id=candidate_id,
            guest_ref=event.guest_ref,
            display_name=profile_data["display_name"],
            room_number=profile_data.get("room_number"),
            allergies=profile_data.get("allergies", []),
            preferences=profile_data.get("preferences", []),
            expires_at=expires_at,
            recognition_status="enrollment_pending",
        )
        recognition_status = await _enroll_candidate_with_worker(
            candidate_id=candidate_id,
            guest_ref=event.guest_ref,
            expires_at=expires_at,
            profile_data=profile_data,
        )
        cohort_manager.set_recognition_status(candidate_id, recognition_status)

        outcome = {
            "action": "admitted",
            "candidate_id": candidate_id,
            "recognition_status": recognition_status,
        }
        cohort_manager.record_event_processed(event.event_id, outcome)
        sse_notifier.notify("roster_change", {"action": "admitted", "timestamp": utc_now_iso()})
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

        removed_tracks = device_manager.remove_guest(public_guest_id(event.guest_ref))
        for stream_id, track_ids in removed_tracks.items():
            for track_id in track_ids:
                await device_manager.send_cue(
                    stream_id,
                    CueMessage(
                        type="clear",
                        stream_id=stream_id,
                        track_id=track_id,
                        status="cleared",
                        cue=None,
                        emitted_at=utc_now_iso(),
                    ).model_dump(),
                )
            await publish_detection_set(stream_id)

        outcome = {
            "action": "departed",
            "guest_ref": event.guest_ref,
            "removed_candidates": removed_candidates,
        }
        cohort_manager.record_event_processed(event.event_id, outcome)
        if removed_candidates:
            sse_notifier.notify("roster_change", {"action": "departed", "timestamp": utc_now_iso()})
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

    if event.status not in {"stable_match", "stable_refresh"}:
        clear_message = CueMessage(
            type="clear",
            stream_id=event.stream_id,
            track_id=event.track_id,
            status="suppressed",
            cue=None,
            emitted_at=utc_now_iso(),
        )
        sent = await device_manager.send_cue(event.stream_id, clear_message.model_dump())
        device_manager.update_detected_person(event.stream_id, event.track_id, None)
        await publish_detection_set(event.stream_id)
        return {
            "status": "suppressed" if sent else "device_not_connected",
            "stream_id": event.stream_id,
        }

    candidate = cohort_manager.get_candidate(event.candidate_id)
    if not candidate:
        logger.info("Match callback for non-active or expired candidate: %s", event.candidate_id)
        clear_message = CueMessage(
            type="clear",
            stream_id=event.stream_id,
            track_id=event.track_id,
            status="suppressed",
            cue=None,
            emitted_at=utc_now_iso(),
        )
        await device_manager.send_cue(event.stream_id, clear_message.model_dump())
        device_manager.update_detected_person(event.stream_id, event.track_id, None)
        await publish_detection_set(event.stream_id)
        return {"status": "ignored", "reason": "candidate_not_active"}

    processing_time = time.monotonic()
    observed_at = device_manager.observation_last_seen(
        event.matched_at, now_monotonic=processing_time
    )
    if observed_at is None:
        return {
            "status": "ignored",
            "reason": "stale_observation",
            "crop_delivered": False,
        }

    current_person = device_manager.get_detected_person(
        event.stream_id, event.track_id, now=processing_time
    )
    crop_delivered = False
    if event.crop_b64 is not None:
        crop_message = FaceCropMessage(
            type="face_crop",
            stream_id=event.stream_id,
            track_id=event.track_id,
            crop_id=event.crop_id,
            image_b64=event.crop_b64,
        )
        crop_delivered = await device_manager.send_cue(
            event.stream_id,
            crop_message.model_dump(exclude_none=True),
        )
        if not crop_delivered:
            return {
                "status": "crop_delivery_failed",
                "stream_id": event.stream_id,
                "track_id": event.track_id,
                "crop_delivered": False,
                "crop_required": True,
            }
    elif current_person is None or current_person.get("crop_id") != event.crop_id:
        return {
            "status": "crop_required",
            "stream_id": event.stream_id,
            "track_id": event.track_id,
            "crop_delivered": False,
            "crop_required": True,
        }

    # Compose compact glanceable cue:
    # 🟢 ✅ ALEX
    # 🔴 ⚠️ PEANUT ALLERGY (if present)
    display_name = candidate["display_name"].upper()
    headline = f"🟢 ✅ {display_name}"

    alert = None
    secondary_color = None
    allergies = candidate.get("allergies", [])
    if allergies:
        allergy_text = str(allergies[0]).strip()
        allergy_lower = allergy_text.lower()
        allergy_icon = allergy_emoji(allergy_lower)
        if (
            allergy_icon
            and "allergy" not in allergy_lower
            and "intoler" not in allergy_lower
            and "sensitiv" not in allergy_lower
        ):
            allergen = allergy_text.upper()
            allergy_text = f"{allergen} ALLERGY"
        allergy_icon = f"{allergy_icon} " if allergy_icon else ""
        alert = f"🔴 ⚠️ {allergy_icon}{allergy_text.upper()}"
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

    detected_person = {
        "guest_id": public_guest_id(candidate["guest_ref"]),
        "display_name": display_name,
        "confidence": event.confidence,
        "preferences": list(candidate.get("preferences", [])),
        "allergies": list(allergies),
        "crop_id": event.crop_id,
        "alert": alert,
    }
    device_manager.update_detected_person(
        event.stream_id,
        event.track_id,
        detected_person,
        now=processing_time,
        last_seen=observed_at,
    )

    if event.status == "stable_refresh":
        if crop_delivered:
            await publish_detection_set(event.stream_id)
        cue_delivered = False
        if current_person is None:
            cue_delivered = await device_manager.send_cue(
                event.stream_id,
                cue_message.model_dump(exclude_none=True),
            )
        return {
            "status": "refreshed",
            "stream_id": event.stream_id,
            "track_id": event.track_id,
            "crop_delivered": crop_delivered,
            "cue_delivered": cue_delivered,
        }

    await publish_detection_set(event.stream_id)
    sent = await device_manager.send_cue(event.stream_id, cue_message.model_dump(exclude_none=True))
    return {
        "status": "delivered" if sent else "device_not_connected",
        "stream_id": event.stream_id,
        "candidate_id": event.candidate_id,
        "crop_delivered": crop_delivered,
    }


@app.post("/internal/v1/debug/frames", status_code=status.HTTP_200_OK, tags=["Internal Debug"])
async def post_debug_frame(
    frame: DebugFrameMessage,
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
):
    """Receive opt-in raw detections and diagnostics from face-worker."""
    if not verify_internal_token(x_internal_token):
        raise HTTPException(status_code=401, detail="Invalid internal service token")
    if not device_manager.owns_stream(frame.device_id, frame.stream_id):
        return {"status": "ignored", "reason": "stream_not_active"}
    if not device_manager.debug_faces_enabled(frame.stream_id):
        return {"status": "ignored", "reason": "debug_disabled"}

    logger.info(
        "face_debug_frame device_id=%s stream_id=%s sequence=%d faces=%d "
        "queue_wait_ms=%.2f detect_ms=%.2f association_ms=%.2f processing_ms=%.2f",
        frame.device_id,
        frame.stream_id,
        frame.sequence,
        len(frame.faces),
        frame.queue_wait_ms,
        frame.detect_ms,
        frame.association_ms,
        frame.processing_ms,
    )
    await device_manager.send_cue(frame.stream_id, frame.model_dump(exclude_none=True))
    return {"status": "delivered", "face_count": len(frame.faces)}


@app.websocket("/v1/video/stream/{device_id}")
@app.websocket("/v1/devices/{device_id}/stream")
async def device_stream_endpoint(
    websocket: WebSocket,
    device_id: str,
    token: Optional[str] = Query(None),
):
    """Authenticated WebSocket for paired phone companion app / frame replay.

    - Authenticates explicitly via query parameter or Authorization header
    - Accepts frame metadata and binary JPEG or JPEG XL frames
    - Forwards transient frames via internal HTTP to face-worker
    - Pushes per-track cues, transient face crops, and current detection sets to the phone
    - Cleans up session and stream state upon disconnect
    """
    # Check authentication
    auth_header = websocket.headers.get("authorization", "")
    bearer_token = None
    if auth_header.lower().startswith("bearer "):
        bearer_token = auth_header[7:].strip()

    requested_protocols = [
        value.strip()
        for value in websocket.headers.get("sec-websocket-protocol", "").split(",")
        if value.strip()
    ]
    protocol_token = next(
        (value.removeprefix("device-token.") for value in requested_protocols if value.startswith("device-token.")),
        None,
    )
    candidate_token = token or bearer_token or protocol_token

    if not is_valid_identifier(device_id) or not verify_token(candidate_token):
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Unauthorized: valid device ID and token required",
        )
        return

    selected_protocol = "device-stream-v1" if "device-stream-v1" in requested_protocols else None
    await websocket.accept(subprotocol=selected_protocol)
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
            if message.get("type") == "websocket.disconnect":
                break
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
                    is_new_stream = not device_manager.has_stream(device_message.stream_id)
                    if not device_manager.set_pending_meta(
                        device_id,
                        device_message.model_dump(exclude_none=True),
                    ):
                        await websocket.send_json({"type": "error", "message": "stream_id is already in use"})
                        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                        break
                    if is_new_stream:
                        await device_manager.send_cue(
                            device_message.stream_id,
                            DetectionSetMessage(
                                type="detection_set",
                                stream_id=device_message.stream_id,
                                people=[],
                            ).model_dump(exclude_none=True),
                        )
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
                    device_manager.set_debug_faces(
                        device_message.stream_id,
                        device_message.debug_faces,
                    )
                    await forward_frame_to_worker(
                        device_id=device_id,
                        stream_id=device_message.stream_id,
                        sequence=device_message.sequence,
                        captured_at=device_message.captured_at or utc_now_iso(),
                        frame_bytes=frame_bytes,
                        image_format=device_message.format,
                    )
                    del frame_bytes
                elif device_message.type == "ping":
                    await websocket.send_json({"type": "pong"})
                else:
                    await websocket.send_json({"type": "error", "message": "Unsupported device message"})

            elif "bytes" in message:
                # Raw binary frame preceded by frame_meta
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
                    image_format=meta.get("format", "image/jpeg"),
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
    image_format: str = "image/jpeg",
) -> None:
    """Forward transient frame to face-worker via internal HTTP.

    Never logs or persists the frame payload.
    """
    if len(frame_bytes) > MAX_FRAME_SIZE_BYTES:
        logger.warning("Rejected oversized device frame (%d bytes)", len(frame_bytes))
        return

    logger.info(
        "frame_received device_id=%s stream_id=%s sequence=%s frame_bytes=%d format=%s captured_at=%s",
        device_id,
        stream_id,
        sequence,
        len(frame_bytes),
        image_format,
        captured_at,
    )
    if not http_client:
        return

    headers = {
        "Content-Type": image_format,
        "X-Device-Id": device_id,
        "X-Stream-Id": stream_id,
        "X-Sequence": str(sequence),
        "X-Captured-At": captured_at,
        "X-Internal-Token": INTERNAL_API_TOKEN,
        "X-Debug-Faces": str(device_manager.debug_faces_enabled(stream_id)).lower(),
    }

    debug_enabled = device_manager.debug_faces_enabled(stream_id)
    started_at = time.perf_counter()
    try:
        resp = await http_client.post(
            f"{FACE_WORKER_URL}/internal/v1/frames",
            content=frame_bytes,
            headers=headers,
        )
        forward_ms = (time.perf_counter() - started_at) * 1000
        try:
            worker_result = resp.json()
        except ValueError:
            worker_result = {}
        worker_disposition = worker_result.get("status", "unknown")
        worker_reason = worker_result.get("reason")
        if worker_disposition == "dropped" or resp.status_code >= 400:
            logger.warning(
                "frame_worker_disposition device_id=%s stream_id=%s sequence=%s "
                "worker_status=%s disposition=%s reason=%s lounge_forward_ms=%.2f",
                device_id,
                stream_id,
                sequence,
                resp.status_code,
                worker_disposition,
                worker_reason or "unknown",
                forward_ms,
            )
        if debug_enabled:
            logger.info(
                "frame_handoff device_id=%s stream_id=%s sequence=%s worker_status=%s "
                "worker_disposition=%s worker_reason=%s lounge_forward_ms=%.2f",
                device_id,
                stream_id,
                sequence,
                resp.status_code,
                worker_disposition,
                worker_reason or "none",
                forward_ms,
            )
            await device_manager.send_cue(
                stream_id,
                {
                    "type": "debug_timing",
                    "stream_id": stream_id,
                    "sequence": sequence,
                    "lounge_forward_ms": forward_ms,
                    "worker_status": resp.status_code,
                    "worker_disposition": worker_disposition,
                    "worker_reason": worker_reason,
                },
            )
        if resp.status_code not in (200, 202):
            logger.warning("Face worker returned status %s for frame handoff", resp.status_code)
    except Exception as e:
        forward_ms = (time.perf_counter() - started_at) * 1000
        if debug_enabled:
            logger.warning(
                "frame_handoff_failed device_id=%s stream_id=%s sequence=%s lounge_forward_ms=%.2f error=%s",
                device_id,
                stream_id,
                sequence,
                forward_ms,
                e,
            )
            await device_manager.send_cue(
                stream_id,
                {
                    "type": "debug_timing",
                    "stream_id": stream_id,
                    "sequence": sequence,
                    "lounge_forward_ms": forward_ms,
                    "error": "Face worker handoff failed",
                },
            )
        else:
            logger.warning("Failed to forward frame to face-worker: %s", e)
