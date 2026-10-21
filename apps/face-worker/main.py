"""FastAPI service for transient face detection and candidate matching."""

import base64
import hmac
import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional
from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    status,
)

# Ensure local module directory and repo root are in path
MODULE_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODULE_DIR.parent.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import asyncio
from contracts.models import CandidateEnrollment, is_valid_identifier
from vision import InvalidImage, InsightFaceEngine
from worker import (
    MATCH_MARGIN,
    MATCH_THRESHOLD,
    MAX_FRAME_SIZE_BYTES,
    STABLE_FRAME_COUNT,
    STABLE_MATCH_COUNT,
    cv_worker_loop,
    enqueue_frame,
    enroll_candidate,
    get_candidate,
    get_stats,
    list_candidate_ids,
    remove_candidate,
    set_face_engine,
    validate_frame,
)

# Send application diagnostics, including worker progress, to container logs.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("face_worker")

FACE_RECOGNITION_ENABLED = os.environ.get("FACE_RECOGNITION_ENABLED", "false").lower() in {
    "1", "true", "yes", "on"
}
FACE_MODELS_DIR = os.environ.get("FACE_MODELS_DIR", "/models/insightface")
FACE_EXECUTION_PROVIDER = os.environ.get("FACE_EXECUTION_PROVIDER", "cpu")
FACE_PROCESS_STARTED_AT = time.perf_counter()
FACE_SERVICE_STARTUP_MS: Optional[float] = None
FACE_MODEL_INITIALIZATION_MS: Optional[float] = None
FACE_MODEL_RUNTIME: Optional[dict] = None
FACE_MODEL_CACHE_WARM_AT_START: Optional[bool] = None


def _model_cache_is_warm() -> bool:
    model_dir = Path(FACE_MODELS_DIR) / "models" / "buffalo_l"
    required_models = ("det_10g.onnx", "w600k_r50.onnx")
    return all(
        (model_dir / model_name).is_file()
        and (model_dir / model_name).stat().st_size > 0
        for model_name in required_models
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global FACE_MODEL_INITIALIZATION_MS, FACE_MODEL_RUNTIME
    global FACE_MODEL_CACHE_WARM_AT_START, FACE_SERVICE_STARTUP_MS
    FACE_MODEL_CACHE_WARM_AT_START = _model_cache_is_warm()
    logger.info(
        "service_starting recognition_enabled=%s match_threshold=%.3f margin_required=%.3f "
        "stable_confirmation=%s_of_%s model_cache_warm_at_start=%s",
        FACE_RECOGNITION_ENABLED,
        MATCH_THRESHOLD,
        MATCH_MARGIN,
        STABLE_MATCH_COUNT,
        STABLE_FRAME_COUNT,
        FACE_MODEL_CACHE_WARM_AT_START,
    )
    if FACE_RECOGNITION_ENABLED:
        model_started = time.perf_counter()
        logger.info("model_initialization_started model=buffalo_l models_dir=%s", FACE_MODELS_DIR)
        try:
            engine = await asyncio.to_thread(InsightFaceEngine, FACE_MODELS_DIR)
        except Exception:
            logger.exception("model_initialization_failed model=buffalo_l")
            raise
        set_face_engine(engine)
        FACE_MODEL_INITIALIZATION_MS = (time.perf_counter() - model_started) * 1000
        FACE_MODEL_RUNTIME = engine.runtime_info
        logger.info(
            "model_runtime requested_provider=%s available_providers=%s "
            "configured_providers=%s providers_by_model=%s coreml_compute_units=%s "
            "coreml_profile_compute_plan=%s coreml_session_count=%s",
            FACE_MODEL_RUNTIME["requested_mode"],
            FACE_MODEL_RUNTIME["available_providers"],
            FACE_MODEL_RUNTIME["configured_providers"],
            FACE_MODEL_RUNTIME["providers_by_model"],
            FACE_MODEL_RUNTIME["coreml_compute_units"],
            FACE_MODEL_RUNTIME["coreml_profile_compute_plan"],
            FACE_MODEL_RUNTIME["coreml_session_count"],
        )
        logger.info(
            "model_ready model=buffalo_l elapsed_seconds=%.2f",
            FACE_MODEL_INITIALIZATION_MS / 1000,
        )
    else:
        logger.warning("face_recognition_disabled frames_will_not_be_matched=true")

    FACE_SERVICE_STARTUP_MS = (time.perf_counter() - FACE_PROCESS_STARTED_AT) * 1000
    logger.info(
        "service_ready startup_ms=%.2f model_initialization_ms=%s "
        "model_cache_warm_at_start=%s",
        FACE_SERVICE_STARTUP_MS,
        "n/a"
        if FACE_MODEL_INITIALIZATION_MS is None
        else f"{FACE_MODEL_INITIALIZATION_MS:.2f}",
        FACE_MODEL_CACHE_WARM_AT_START,
    )
    worker_task = asyncio.create_task(cv_worker_loop())
    logger.info("processing_loop_started")
    yield
    logger.info("processing_loop_stopping")
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    set_face_engine(None)


app = FastAPI(
    title="Face Worker Service",
    description="Local face detection and transient active-cohort matching service",
    version="0.1.0",
    lifespan=lifespan,
)


def require_internal_token(
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
) -> None:
    """Protect service-only endpoints published on the POC LAN ports."""
    expected = os.environ.get("INTERNAL_API_TOKEN", "").strip()
    if not expected or not x_internal_token or not hmac.compare_digest(
        expected, x_internal_token.strip()
    ):
        raise HTTPException(status_code=401, detail="Invalid internal service token")


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint for Docker Compose."""
    stats = get_stats()
    return {
        "status": "ok",
        "service": "face-worker",
        "recognition_enabled": FACE_RECOGNITION_ENABLED,
        "requested_execution_provider": FACE_EXECUTION_PROVIDER,
        "service_startup_ms": FACE_SERVICE_STARTUP_MS,
        "model_initialization_ms": FACE_MODEL_INITIALIZATION_MS,
        "model_cache_warm_at_start": FACE_MODEL_CACHE_WARM_AT_START,
        "model_runtime": FACE_MODEL_RUNTIME,
        "match_threshold": MATCH_THRESHOLD,
        "match_margin": MATCH_MARGIN,
        "stable_frame_count": STABLE_FRAME_COUNT,
        "stable_match_count": STABLE_MATCH_COUNT,
        **stats,
    }


@app.put(
    "/internal/v1/candidates/{candidate_id}",
    status_code=status.HTTP_200_OK,
    tags=["Candidate Cohort"],
)
async def put_candidate(
    candidate_id: str,
    payload: CandidateEnrollment,
    _: None = Depends(require_internal_token),
):
    """Derive and retain a face template for an opaque active candidate."""
    if not is_valid_identifier(candidate_id):
        raise HTTPException(status_code=400, detail="Invalid candidate_id")
    if payload.candidate_id != candidate_id:
        raise HTTPException(
            status_code=400,
            detail="candidate_id in path does not match body",
        )

    photos_b64 = payload.photos_b64 or ([payload.photo_b64] if payload.photo_b64 else [])
    photo_bytes_list = []
    for index, photo_b64 in enumerate(photos_b64):
        try:
            photo_bytes = base64.b64decode(photo_b64, validate=True)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base64 in reference photo {index + 1}",
            )
        is_valid, error_msg = validate_frame(photo_bytes)
        if not is_valid:
            status_code = 413 if "exceeds maximum limit" in (error_msg or "") else 400
            raise HTTPException(status_code=status_code, detail=error_msg)
        photo_bytes_list.append(photo_bytes)

    enrollment_started = time.perf_counter()
    logger.info(
        "candidate_enrollment_started candidate_id=%s reference_photos=%s model_ready=%s",
        candidate_id,
        len(photo_bytes_list),
        get_stats()["face_engine_ready"],
    )
    try:
        # Keep InsightFace inference out of the ASGI event loop. Its model lock
        # serializes enrollment with live detection while HTTP/health handlers
        # remain responsive.
        template_status = await asyncio.to_thread(
            enroll_candidate,
            candidate_id,
            photo_bytes_list,
            payload.expires_at,
        )
    except InvalidImage as exc:
        logger.warning(
            "candidate_enrollment_failed candidate_id=%s reason=invalid_image error=%s",
            candidate_id,
            exc,
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.info(
        "candidate_enrolled candidate_id=%s reference_photos=%s template_status=%s elapsed_ms=%.2f",
        candidate_id,
        len(photo_bytes_list),
        template_status,
        (time.perf_counter() - enrollment_started) * 1000,
    )
    return {
        "status": "enrolled",
        "candidate_id": candidate_id,
        "expires_at": payload.expires_at,
        "template_status": template_status,
    }


@app.delete(
    "/internal/v1/candidates/{candidate_id}",
    status_code=status.HTTP_200_OK,
    tags=["Candidate Cohort"],
)
async def delete_candidate(
    candidate_id: str,
    _: None = Depends(require_internal_token),
):
    """Remove candidate presence metadata from the in-memory cohort."""
    if not is_valid_identifier(candidate_id):
        raise HTTPException(status_code=400, detail="Invalid candidate_id")
    existed = remove_candidate(candidate_id)
    logger.info("candidate_removed candidate_id=%s existed=%s", candidate_id, existed)
    return {"status": "removed", "candidate_id": candidate_id, "existed": existed}


@app.get(
    "/internal/v1/candidates",
    response_model=List[str],
    tags=["Candidate Cohort"],
)
async def list_candidates(_: None = Depends(require_internal_token)):
    """List opaque candidate IDs currently in memory."""
    return list_candidate_ids()


@app.get(
    "/internal/v1/candidates/{candidate_id}",
    tags=["Candidate Cohort"],
)
async def get_candidate_status(
    candidate_id: str,
    _: None = Depends(require_internal_token),
):
    """Return transient enrollment status for lounge-control reconciliation."""
    if not is_valid_identifier(candidate_id):
        raise HTTPException(status_code=400, detail="Invalid candidate_id")
    candidate = get_candidate(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"candidate_id": candidate_id, **candidate}


@app.post(
    "/internal/v1/frames",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Frame Ingress"],
)
async def post_frame(
    request: Request,
    x_stream_id: Optional[str] = Header(None, alias="X-Stream-Id"),
    x_device_id: Optional[str] = Header(None, alias="X-Device-Id"),
    x_sequence: Optional[int] = Header(None, alias="X-Sequence"),
    x_captured_at: Optional[str] = Header(None, alias="X-Captured-At"),
    x_debug_faces: bool = Header(False, alias="X-Debug-Faces"),
    _: None = Depends(require_internal_token),
):
    """Ingest a binary JPEG or JPEG XL frame.

    Rejects malformed or oversized input; queues valid frames on a bounded
    per-stream queue that drops stale frames under backpressure.
    Discards frame payloads after validation (never persists to disk).
    """
    if not x_stream_id:
        logger.warning("frame_rejected_missing_stream_id device_id=%s", x_device_id or "unknown")
        raise HTTPException(status_code=400, detail="Missing required X-Stream-Id header")
    if not x_device_id:
        logger.warning("frame_rejected_missing_device_id stream_id=%s", x_stream_id)
        raise HTTPException(status_code=400, detail="Missing required X-Device-Id header")
    if not is_valid_identifier(x_stream_id) or not is_valid_identifier(x_device_id):
        logger.warning(
            "frame_rejected_invalid_identifier device_id=%s stream_id=%s",
            x_device_id,
            x_stream_id,
        )
        raise HTTPException(status_code=400, detail="Invalid device or stream identifier")
    image_format = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if image_format not in {"image/jpeg", "image/jxl"}:
        logger.warning(
            "frame_rejected_content_type device_id=%s stream_id=%s content_type=%s",
            x_device_id,
            x_stream_id,
            request.headers.get("content-type", "missing"),
        )
        raise HTTPException(
            status_code=415,
            detail="Content-Type must be image/jpeg or image/jxl",
        )

    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_FRAME_SIZE_BYTES:
                logger.warning(
                    "frame_rejected_oversized_content_length device_id=%s stream_id=%s "
                    "content_length=%s max_bytes=%s",
                    x_device_id,
                    x_stream_id,
                    content_length,
                    MAX_FRAME_SIZE_BYTES,
                )
                raise HTTPException(status_code=413, detail="Frame exceeds maximum size")
        except ValueError:
            logger.warning(
                "frame_rejected_invalid_content_length device_id=%s stream_id=%s",
                x_device_id,
                x_stream_id,
            )
            raise HTTPException(status_code=400, detail="Invalid Content-Length")

    chunks = []
    total_bytes = 0
    async for chunk in request.stream():
        total_bytes += len(chunk)
        if total_bytes > MAX_FRAME_SIZE_BYTES:
            logger.warning(
                "frame_rejected_oversized_body device_id=%s stream_id=%s bytes=%s max_bytes=%s",
                x_device_id,
                x_stream_id,
                total_bytes,
                MAX_FRAME_SIZE_BYTES,
            )
            raise HTTPException(status_code=413, detail="Frame exceeds maximum size")
        chunks.append(chunk)
    body = b"".join(chunks)
    is_valid, error_msg = validate_frame(body, image_format)
    if not is_valid:
        logger.warning(
            "frame_rejected_invalid_image device_id=%s stream_id=%s sequence=%s format=%s "
            "bytes=%s reason=%s",
            x_device_id,
            x_stream_id,
            x_sequence,
            image_format,
            len(body),
            error_msg,
        )
        if "exceeds maximum limit" in (error_msg or ""):
            raise HTTPException(status_code=413, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    accepted = enqueue_frame(
        stream_id=x_stream_id,
        device_id=x_device_id,
        sequence=x_sequence,
        captured_at=x_captured_at or "",
        frame_bytes=body,
        debug_faces=x_debug_faces,
        image_format=image_format,
    )

    return {
        "status": "accepted" if accepted else "dropped",
        "reason": None if accepted else "stale_or_out_of_order",
        "stream_id": x_stream_id,
        "sequence": x_sequence,
    }
