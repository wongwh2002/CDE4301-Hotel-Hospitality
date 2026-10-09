"""FastAPI service for transient face detection and candidate matching."""

import base64
import hmac
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status

# Ensure local module directory and repo root are in path
MODULE_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODULE_DIR.parent.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import asyncio
from contracts.models import CandidateEnrollment, is_valid_identifier
from download_models import ensure_models
from vision import InvalidImage, OpenCVFaceEngine
from worker import (
    MAX_FRAME_SIZE_BYTES,
    cv_worker_loop,
    enqueue_frame,
    enroll_candidate,
    get_stats,
    list_candidate_ids,
    remove_candidate,
    set_face_engine,
    validate_frame,
)

FACE_RECOGNITION_ENABLED = os.environ.get("FACE_RECOGNITION_ENABLED", "false").lower() in {
    "1", "true", "yes", "on"
}
FACE_MODELS_DIR = os.environ.get("FACE_MODELS_DIR", "/models")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if FACE_RECOGNITION_ENABLED:
        model_paths = await asyncio.to_thread(ensure_models, FACE_MODELS_DIR)
        engine = await asyncio.to_thread(
            OpenCVFaceEngine,
            model_paths["yunet.onnx"],
            model_paths["sface.onnx"],
        )
        set_face_engine(engine)

    worker_task = asyncio.create_task(cv_worker_loop())
    yield
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    set_face_engine(None)


app = FastAPI(
    title="Face Worker Service",
    description="Interface and validation skeleton for face detection and matching",
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

    photo_bytes = b""
    if payload.photo_b64:
        try:
            photo_bytes = base64.b64decode(payload.photo_b64, validate=True)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 in photo_b64")
        is_valid, error_msg = validate_frame(photo_bytes)
        if not is_valid:
            status_code = 413 if "exceeds maximum limit" in (error_msg or "") else 400
            raise HTTPException(status_code=status_code, detail=error_msg)

    try:
        template_status = enroll_candidate(
            candidate_id=candidate_id,
            photo_bytes=photo_bytes,
            expires_at=payload.expires_at,
        )
    except InvalidImage as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
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
    return {"status": "removed", "candidate_id": candidate_id, "existed": existed}


@app.get(
    "/internal/v1/candidates",
    response_model=List[str],
    tags=["Candidate Cohort"],
)
async def list_candidates(_: None = Depends(require_internal_token)):
    """List opaque candidate IDs currently in memory."""
    return list_candidate_ids()


@app.post(
    "/internal/v1/frames",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Frame Ingress"],
)
async def post_frame(
    request: Request,
    x_stream_id: Optional[str] = Header(None, alias="X-Stream-Id"),
    x_device_id: Optional[str] = Header(None, alias="X-Device-Id"),
    x_sequence: Optional[int] = Header(0, alias="X-Sequence"),
    x_captured_at: Optional[str] = Header(None, alias="X-Captured-At"),
    _: None = Depends(require_internal_token),
):
    """Ingest a binary JPEG frame.

    Rejects malformed or oversized input; queues valid frames on a bounded
    per-stream queue that drops stale frames under backpressure.
    Discards frame payloads after validation (never persists to disk).
    """
    if not x_stream_id:
        raise HTTPException(status_code=400, detail="Missing required X-Stream-Id header")
    if not x_device_id:
        raise HTTPException(status_code=400, detail="Missing required X-Device-Id header")
    if not is_valid_identifier(x_stream_id) or not is_valid_identifier(x_device_id):
        raise HTTPException(status_code=400, detail="Invalid device or stream identifier")
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "image/jpeg":
        raise HTTPException(status_code=415, detail="Content-Type must be image/jpeg")

    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_FRAME_SIZE_BYTES:
                raise HTTPException(status_code=413, detail="Frame exceeds maximum size")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Content-Length")

    chunks = []
    total_bytes = 0
    async for chunk in request.stream():
        total_bytes += len(chunk)
        if total_bytes > MAX_FRAME_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="Frame exceeds maximum size")
        chunks.append(chunk)
    body = b"".join(chunks)
    is_valid, error_msg = validate_frame(body)
    if not is_valid:
        if "exceeds maximum limit" in (error_msg or ""):
            raise HTTPException(status_code=413, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    enqueue_frame(
        stream_id=x_stream_id,
        device_id=x_device_id,
        sequence=x_sequence or 0,
        captured_at=x_captured_at or "",
        frame_bytes=body,
    )

    return {
        "status": "accepted",
        "stream_id": x_stream_id,
        "sequence": x_sequence,
    }
