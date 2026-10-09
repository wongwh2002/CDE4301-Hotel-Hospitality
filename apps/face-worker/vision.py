"""OpenCV YuNet/SFace pipeline for transient face detection and matching.

This is a POC baseline. Thresholds need evaluation on consented, representative
images before any real-world use; an uncertain result never becomes a match.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
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


class OpenCVFaceEngine:
    """CPU-first face detector and embedding model backed by OpenCV DNN."""

    def __init__(self, yunet_path: str | Path, sface_path: str | Path):
        import cv2

        self._cv2 = cv2
        self._detector = cv2.FaceDetectorYN.create(
            str(yunet_path), "", (320, 320), 0.80, 0.30, 5000
        )
        self._recognizer = cv2.FaceRecognizerSF.create(str(sface_path), "")

    @staticmethod
    def _decode(image_bytes: bytes):
        import cv2
        import numpy as np

        image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None or image.size == 0:
            raise InvalidImage("JPEG could not be decoded")
        return image

    def detect(self, image_bytes: bytes) -> list[DetectedFace]:
        import numpy as np

        image = self._decode(image_bytes)
        height, width = image.shape[:2]
        self._detector.setInputSize((width, height))
        _, rows = self._detector.detect(image)
        if rows is None:
            return []

        faces: list[DetectedFace] = []
        for row in rows:
            aligned = self._recognizer.alignCrop(image, row)
            feature = np.asarray(self._recognizer.feature(aligned), dtype=np.float32).reshape(-1)
            norm = float(np.linalg.norm(feature))
            if not norm:
                continue
            feature /= norm
            faces.append(
                DetectedFace(
                    bbox=(float(row[0]), float(row[1]), float(row[2]), float(row[3])),
                    embedding=feature,
                    detector_score=float(row[-1]),
                )
            )
        return faces

    def create_template(self, image_bytes: bytes):
        """Return one normalized embedding; reject empty or multi-face photos."""
        faces = self.detect(image_bytes)
        if len(faces) != 1:
            raise FaceCountError(
                f"Reference photo must contain exactly one detectable face; found {len(faces)}"
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
