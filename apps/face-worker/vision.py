"""InsightFace buffalo_l pipeline for transient face detection and matching.

This is a POC baseline. Thresholds need evaluation on consented, representative
images before any real-world use; an uncertain result never becomes a match.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any


class InvalidImage(ValueError):
    """Raised when a JPEG cannot be decoded as an image."""


class FaceCountError(ValueError):
    """Raised when a reference image does not contain exactly one usable face."""


@dataclass(frozen=True)
class DetectedFace:
    bbox: tuple[float, float, float, float]
    embedding: Any
    detector_score: float


class InsightFaceEngine:
    """CPU-first face detector and embedding model backed by InsightFace."""

    def __init__(self, model_root: str | Path):
        import numpy as np
        from insightface.app import FaceAnalysis

        self._np = np
        self._analysis = FaceAnalysis(
            name="buffalo_l",
            root=str(model_root),
            allowed_modules=["detection", "recognition"],
            providers=["CPUExecutionProvider"],
        )
        self._analysis.prepare(ctx_id=-1)
        self._model_lock = Lock()

    @staticmethod
    def _decode(image_bytes: bytes):
        import cv2
        import numpy as np

        image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None or image.size == 0:
            raise InvalidImage("JPEG could not be decoded")
        return image

    def detect(self, image_bytes: bytes) -> list[DetectedFace]:
        image = self._decode(image_bytes)
        faces: list[DetectedFace] = []
        # Lounge matching and direct phone streams share this model instance.
        # Serialize inference to bound contention across incoming frames.
        with self._model_lock:
            detected_faces = self._analysis.get(image)
        for face in detected_faces:
            if face.bbox is None:
                continue
            feature = None
            if face.normed_embedding is not None:
                feature = self._np.asarray(
                    face.normed_embedding, dtype=self._np.float32
                ).reshape(-1)
                norm = float(self._np.linalg.norm(feature))
                if norm:
                    feature /= norm
                else:
                    feature = None
            x1, y1, x2, y2 = (float(value) for value in face.bbox)
            faces.append(
                DetectedFace(
                    bbox=(x1, y1, max(0.0, x2 - x1), max(0.0, y2 - y1)),
                    embedding=feature,
                    detector_score=float(face.det_score or 0.0),
                )
            )
        return faces

    def create_template(self, image_bytes: bytes):
        """Return one normalized embedding; reject empty or multi-face photos."""
        faces = self.detect(image_bytes)
        if len(faces) != 1 or faces[0].embedding is None:
            raise FaceCountError(
                "Reference photo must contain exactly one face with a usable embedding; "
                f"found {len(faces)} detectable face(s)"
            )
        return faces[0].embedding

    @staticmethod
    def cosine_similarity(left, right) -> float:
        import numpy as np

        left_vector = np.asarray(left, dtype=np.float32).reshape(-1)
        right_vector = np.asarray(right, dtype=np.float32).reshape(-1)
        left_norm = float(np.linalg.norm(left_vector))
        right_norm = float(np.linalg.norm(right_vector))
        if not left_norm or not right_norm or left_vector.shape != right_vector.shape:
            return -1.0
        return float(np.dot(left_vector, right_vector) / (left_norm * right_norm))
