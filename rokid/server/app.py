"""Full-frame face identification service. Incoming images are processed in memory only."""
from __future__ import annotations

import io
import logging
import math
import os
import threading
import time
import warnings
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, Header, HTTPException, Query, Request
from PIL import Image, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool
from server.recognition import (
    DEFAULT_MARGIN, DEFAULT_THRESHOLD, MODEL_NAME, FaceResult, InsightFaceRecognizer,
)
from server.audio_preferences import AudioFormatError, GuestBindingError, MAX_AUDIO_BYTES, PipelineError, PreferenceService
from server.preference_store import CaptureConflict

LOG = logging.getLogger("uvicorn.error")
MAX_BYTES = 8 * 1024 * 1024
MAX_PIXELS = 16_000_000
MAX_DISPLAY_FACES = 5
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


def format_display(faces: list[FaceResult]) -> str:
    if not faces:
        return "No face detected"
    counts: dict[str, int] = {}
    for face in faces:
        counts[face.name] = counts.get(face.name, 0) + 1
    names = list(counts.items())
    lines = [
        f"{name} x{count}" if count > 1 else name
        for name, count in names[:MAX_DISPLAY_FACES]
    ]
    if len(names) > MAX_DISPLAY_FACES:
        lines.append(f"+{len(names) - MAX_DISPLAY_FACES} more")
    return "\n".join(lines)


def process_image(recognizer, data: bytes, rotation: int, request_id: str) -> dict:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as source:
                if source.format != "JPEG":
                    raise HTTPException(415, "Expected a JPEG image")
                if source.width * source.height > MAX_PIXELS:
                    raise HTTPException(413, "Image dimensions exceed limit")
                source.load()
                image = source.convert("RGB")
        if rotation:
            image = image.rotate(-rotation, expand=True)
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise HTTPException(413, "Image dimensions exceed limit")
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(400, "Invalid JPEG image")

    started = time.perf_counter()
    bgr = np.asarray(image)[:, :, ::-1].copy()
    faces = recognizer.detect(bgr)
    inference_ms = round((time.perf_counter() - started) * 1000, 1)
    if not faces:
        LOG.info("Face result %s: No face detected (%.1f ms)", request_id, inference_ms)
    else:
        for face in faces:
            if face.similarity is None:
                LOG.info("Face result %s: %s (no enrolled templates)", request_id, face.name)
            else:
                LOG.info(
                    "Face result %s: %s (cosine similarity %.3f; detection %.1f%%)",
                    request_id, face.name, face.similarity, face.detection_confidence * 100,
                )
    return {
        "faces": [
            {
                "name": face.name,
                "similarity": face.similarity,
                "runner_up_similarity": face.runner_up_similarity,
                "box": face.box,
                "detection_confidence": face.detection_confidence,
            }
            for face in faces
        ],
        "display": format_display(faces),
        "image_width": image.width,
        "image_height": image.height,
        "inference_ms": inference_ms,
    }


def create_app(recognizer=None, threshold: float | None = None, margin: float | None = None, preference_service=None) -> FastAPI:
    match_threshold = float(os.getenv("FACE_MATCH_THRESHOLD", str(DEFAULT_THRESHOLD))) if threshold is None else threshold
    match_margin = float(os.getenv("FACE_MATCH_MARGIN", str(DEFAULT_MARGIN))) if margin is None else margin
    if not math.isfinite(match_threshold) or not -1 <= match_threshold <= 1:
        raise ValueError("FACE_MATCH_THRESHOLD must be between -1 and 1")
    if not math.isfinite(match_margin) or not 0 <= match_margin <= 2:
        raise ValueError("FACE_MATCH_MARGIN must be between 0 and 2")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.recognizer = (
            recognizer if recognizer is not None
            else await run_in_threadpool(InsightFaceRecognizer, match_threshold, match_margin)
        )
        LOG.info("Face recognizer ready; model=%s cosine threshold=%.3f margin=%.3f", MODEL_NAME, match_threshold, match_margin)
        app.state.preference_service = (await run_in_threadpool(PreferenceService.from_environment)
            if preference_service is None else preference_service)
        try:
            yield
        finally:
            if app.state.preference_service:
                app.state.preference_service.close()

    app = FastAPI(title="Rokid face identification", lifespan=lifespan)
    app.state.inference_lock = threading.Lock()

    @app.get("/health")
    async def health():
        return {
            "status": "ready",
            "protocol_version": 2,
            "match_threshold": match_threshold,
            "match_margin": match_margin,
            "model": MODEL_NAME,
            "providers": getattr(app.state.recognizer, "providers", {}),
            "gallery_names": len(getattr(app.state.recognizer, "gallery", {})),
            "gallery_templates": sum(map(len, getattr(app.state.recognizer, "gallery", {}).values())),
            "audio_preferences": app.state.preference_service.health() if app.state.preference_service else {"enabled": False},
        }

    @app.post("/detect")
    async def detect(
        request: Request,
        rotation: int = 0,
        request_id: str = Query(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9-]+$"),
    ):
        if rotation not in (0, 90, 180, 270):
            raise HTTPException(422, "rotation must be 0, 90, 180, or 270")
        if request.headers.get("content-type", "").split(";")[0].strip() != "image/jpeg":
            raise HTTPException(415, "Content-Type must be image/jpeg")
        size = request.headers.get("content-length")
        if size is not None:
            try:
                length = int(size)
            except ValueError:
                raise HTTPException(400, "Invalid Content-Length")
            if length < 0:
                raise HTTPException(400, "Invalid Content-Length")
            if length > MAX_BYTES:
                raise HTTPException(413, "Image exceeds 8 MiB")
        if not app.state.inference_lock.acquire(blocking=False):
            raise HTTPException(503, "Recognizer busy", headers={"Retry-After": "2"})
        try:
            data = bytearray()
            async for chunk in request.stream():
                data.extend(chunk)
                if len(data) > MAX_BYTES:
                    raise HTTPException(413, "Image exceeds 8 MiB")
            if not data:
                raise HTTPException(400, "Empty image")
            result = await run_in_threadpool(
                process_image, app.state.recognizer, bytes(data), rotation, request_id
            )
            service = app.state.preference_service
            guest_binding = None
            if service and len(result["faces"]) == 1:
                name = result["faces"][0]["name"]
                if name.strip() and name.casefold() != "unknown":
                    guest_binding = service.bindings.issue(name)
            return {
                "protocol_version": 2,
                "request_id": request_id,
                "match_threshold": match_threshold,
                "match_margin": match_margin,
                "model": MODEL_NAME,
                "preference_guest": guest_binding,
                **result,
            }
        except HTTPException:
            raise
        except Exception:
            LOG.exception("Face recognition failed")
            raise HTTPException(500, "Face recognition failed")
        finally:
            app.state.inference_lock.release()

    @app.post("/audio/preferences")
    async def capture_preferences(request: Request,
        request_id: str = Query(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9-]+$"),
        guest_token: str = Header(alias="X-Guest-Token", min_length=1, max_length=128)):
        service = app.state.preference_service
        if not service:
            raise HTTPException(503, "Audio preferences are disabled")
        if request.headers.get("content-type", "").split(";")[0].strip() != "audio/wav":
            raise HTTPException(415, "Content-Type must be audio/wav")
        try:
            service.bindings.resolve(guest_token)
        except GuestBindingError as error:
            raise HTTPException(401, str(error)) from None
        if not service.extractor.configured:
            raise HTTPException(503, "Gemini API key is not configured on the server")
        if not service.lock.acquire(blocking=False):
            raise HTTPException(503, "Audio preference processing busy", headers={"Retry-After": "2"})
        try:
            size = request.headers.get("content-length")
            if size is not None:
                try:
                    if int(size) < 0: raise ValueError()
                    if int(size) > MAX_AUDIO_BYTES: raise HTTPException(413, "Audio exceeds limit")
                except ValueError:
                    raise HTTPException(400, "Invalid Content-Length") from None
            data = bytearray()
            async for chunk in request.stream():
                data.extend(chunk)
                if len(data) > MAX_AUDIO_BYTES: raise HTTPException(413, "Audio exceeds limit")
            return await run_in_threadpool(service.process, bytes(data), guest_token, request_id)
        except GuestBindingError as error:
            raise HTTPException(401, str(error)) from None
        except AudioFormatError as error:
            raise HTTPException(422, str(error)) from None
        except CaptureConflict as error:
            raise HTTPException(409, str(error)) from None
        except PipelineError as error:
            LOG.warning("Preference capture %s failed stage=%s provider_code=%s", request_id, error.stage, error.provider_code)
            status = 503 if error.provider_code in (429,500,502,503,504) else 502
            raise HTTPException(status, {"error": "Preference processing failed", "stage": error.stage,
                "provider_code": error.provider_code}, headers={"Retry-After":"2"} if status == 503 else None) from None
        finally:
            service.lock.release()

    @app.get("/guests")
    async def guests():
        service = app.state.preference_service
        if not service: raise HTTPException(503, "Audio preferences are disabled")
        return {"guests": await run_in_threadpool(service.store.guests)}

    @app.get("/guests/{guest_id}/preferences")
    async def guest_preferences(guest_id: str):
        service = app.state.preference_service
        if not service: raise HTTPException(503, "Audio preferences are disabled")
        profiles = await run_in_threadpool(service.store.guests)
        profile = next((profile for profile in profiles if profile["guest_id"] == guest_id), None)
        if profile is None: raise HTTPException(404, "Guest not found")
        return profile

    return app


app = create_app()
