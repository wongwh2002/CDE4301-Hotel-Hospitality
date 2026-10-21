"""Full-frame face identification service. Incoming images are processed in memory only."""
from __future__ import annotations

import io
import logging
import math
import os
import threading
import time
import warnings
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException, Query, Request
from PIL import Image, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

LOG = logging.getLogger("uvicorn.error")
MAX_BYTES = 8 * 1024 * 1024
MAX_PIXELS = 16_000_000
MAX_DISPLAY_FACES = 5
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


@dataclass(frozen=True)
class FaceResult:
    name: str
    similarity: float | None
    box: dict[str, int]
    detection_confidence: float


class OpenCvFaceRecognizer:
    """YuNet face detection plus SFace embeddings and a filename-based face gallery."""

    def __init__(self, threshold: float):
        import cv2

        self.cv2 = cv2
        self.threshold = threshold
        server_dir = Path(__file__).parent
        models_dir = Path(os.getenv("FACE_MODELS_DIR", str(server_dir / "models")))
        detector_path = Path(os.getenv(
            "FACE_DETECTION_MODEL", str(models_dir / "face_detection_yunet_2023mar.onnx")
        ))
        recognizer_path = Path(os.getenv(
            "FACE_RECOGNITION_MODEL", str(models_dir / "face_recognition_sface_2021dec.onnx")
        ))
        for model_path in (detector_path, recognizer_path):
            if not model_path.is_file():
                raise FileNotFoundError(
                    f"Missing OpenCV model {model_path}. Run: python server/setup.py"
                )

        self.detector = cv2.FaceDetectorYN.create(
            str(detector_path), "", (320, 320),
            float(os.getenv("FACE_DETECTION_CONFIDENCE", "0.80")), 0.3, 5000,
        )
        self.recognizer = cv2.FaceRecognizerSF.create(str(recognizer_path), "")
        self.gallery_dir = Path(os.getenv("FACE_GALLERY", str(server_dir / "faces")))
        self.gallery_dir.mkdir(parents=True, exist_ok=True)
        self.gallery: dict[str, list[np.ndarray]] = defaultdict(list)
        self._load_gallery()
        # Catch broken/incompatible models before reporting /health as ready.
        self._detect(np.zeros((320, 320, 3), dtype=np.uint8))

    def _detect(self, image: np.ndarray):
        height, width = image.shape[:2]
        self.detector.setInputSize((width, height))
        _, faces = self.detector.detect(image)
        return [] if faces is None else faces

    def _feature(self, image: np.ndarray, face: np.ndarray) -> np.ndarray:
        aligned = self.recognizer.alignCrop(image, face)
        return self.recognizer.feature(aligned)

    def _load_gallery(self) -> None:
        supported = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        for path in sorted(self.gallery_dir.iterdir()):
            if not path.is_file() or path.suffix.lower() not in supported:
                continue
            image = self.cv2.imread(str(path), self.cv2.IMREAD_COLOR)
            if image is None:
                LOG.warning("Skipping unreadable gallery image: %s", path.name)
                continue
            faces = self._detect(image)
            if len(faces) == 0:
                LOG.warning("No face found in gallery image: %s", path.name)
                continue
            # One enrollment image can contain several faces; use its largest face.
            face = max(faces, key=lambda item: float(item[2] * item[3]))
            self.gallery[path.stem].append(self._feature(image, face))
        LOG.info(
            "Loaded %d face templates for %d names from %s",
            sum(map(len, self.gallery.values())), len(self.gallery), self.gallery_dir,
        )

    def detect(self, image: np.ndarray) -> list[FaceResult]:
        results = []
        height, width = image.shape[:2]
        for face in self._detect(image):
            x, y, box_width, box_height = (float(value) for value in face[:4])
            x1 = max(0, min(width, round(x)))
            y1 = max(0, min(height, round(y)))
            x2 = max(x1, min(width, round(x + box_width)))
            y2 = max(y1, min(height, round(y + box_height)))
            feature = self._feature(image, face)
            best_name = "Unknown"
            best_score: float | None = None
            for name, templates in self.gallery.items():
                score = max(
                    float(self.recognizer.match(
                        feature, template, self.cv2.FaceRecognizerSF_FR_COSINE
                    ))
                    for template in templates
                )
                if math.isfinite(score) and (best_score is None or score > best_score):
                    best_name, best_score = name, score
            if best_score is None or best_score < self.threshold:
                best_name = "Unknown"
            results.append(FaceResult(
                best_name, best_score,
                {"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1},
                float(face[14]),
            ))
        return results


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


def create_app(recognizer=None, threshold: float | None = None) -> FastAPI:
    match_threshold = float(os.getenv("FACE_MATCH_THRESHOLD", "0.363")) if threshold is None else threshold
    if not math.isfinite(match_threshold) or not -1 <= match_threshold <= 1:
        raise ValueError("FACE_MATCH_THRESHOLD must be between -1 and 1")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.recognizer = (
            recognizer if recognizer is not None
            else await run_in_threadpool(OpenCvFaceRecognizer, match_threshold)
        )
        LOG.info("Face recognizer ready; cosine similarity threshold %.3f", match_threshold)
        yield

    app = FastAPI(title="Rokid face identification", lifespan=lifespan)
    app.state.inference_lock = threading.Lock()

    @app.get("/health")
    async def health():
        return {
            "status": "ready",
            "protocol_version": 2,
            "match_threshold": match_threshold,
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
            return {
                "protocol_version": 2,
                "request_id": request_id,
                "match_threshold": match_threshold,
                **result,
            }
        except HTTPException:
            raise
        except Exception:
            LOG.exception("Face recognition failed")
            raise HTTPException(500, "Face recognition failed")
        finally:
            app.state.inference_lock.release()

    return app


app = create_app()
