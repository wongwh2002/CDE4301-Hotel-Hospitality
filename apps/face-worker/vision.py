"""InsightFace buffalo_l pipeline for transient face detection and matching.

This is a POC baseline. Thresholds need evaluation on consented, representative
images before any real-world use; an uncertain result never becomes a match.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Optional


class InvalidImage(ValueError):
    """Raised when an incoming JPEG or JPEG XL frame cannot be decoded."""


class FaceCountError(ValueError):
    """Raised when a reference image does not contain exactly one usable face."""


@dataclass(frozen=True)
class DetectedFace:
    bbox: tuple[float, float, float, float]
    embedding: Any
    detector_score: float
    crop_jpeg: Optional[bytes] = None
    crop_signature: Optional[int] = None


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
    def _decode(image_bytes: bytes, image_format: str = "image/jpeg"):
        import numpy as np
        import cv2

        if image_format == "image/jxl":
            # The Docker image builds OpenCV against libjxl, so prefer the same
            # decoder used for JPEG. Keep imagecodecs as a fallback for local
            # Python environments whose prebuilt OpenCV wheel lacks JXL.
            encoded = np.frombuffer(image_bytes, dtype=np.uint8)
            image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
            if image is not None and image.size:
                return image

            import imagecodecs

            try:
                image = imagecodecs.jpegxl_decode(image_bytes)
            except Exception as exc:
                raise InvalidImage("JPEG XL could not be decoded") from exc
            if image is None or image.size == 0:
                raise InvalidImage("JPEG XL decoded to an empty image")
            if image.dtype != np.uint8:
                raise InvalidImage(
                    f"JPEG XL must decode to 8-bit pixels, got {image.dtype}"
                )
            if image.ndim == 2:
                image = np.repeat(image[:, :, None], 3, axis=2)
            elif image.ndim == 3:
                channels = image.shape[2]
                if channels in (1, 2):
                    image = np.repeat(image[:, :, :1], 3, axis=2)
                elif channels == 4:
                    image = image[:, :, :3]
                elif channels != 3:
                    raise InvalidImage(
                        f"JPEG XL must have 1, 2, 3, or 4 channels, got {channels}"
                    )
            else:
                raise InvalidImage(
                    f"JPEG XL must decode to a 2D or 3D image, got {image.ndim} dimensions"
                )
            # imagecodecs returns RGB(A); InsightFace/OpenCV expects BGR.
            return np.ascontiguousarray(image[:, :, :3][:, :, ::-1])

        if image_format != "image/jpeg":
            raise InvalidImage(f"Unsupported image format: {image_format}")

        image = cv2.imdecode(
            np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR
        )
        if image is None or image.size == 0:
            raise InvalidImage("JPEG could not be decoded")
        return image

    def detect(
        self, image_bytes: bytes, image_format: str = "image/jpeg"
    ) -> list[DetectedFace]:
        import cv2

        image = self._decode(image_bytes, image_format)
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
            bbox = (x1, y1, max(0.0, x2 - x1), max(0.0, y2 - y1))
            crop_jpeg, crop_signature = self._encode_face_crop(cv2, image, bbox)
            faces.append(
                DetectedFace(
                    bbox=bbox,
                    embedding=feature,
                    detector_score=float(face.det_score or 0.0),
                    crop_jpeg=crop_jpeg,
                    crop_signature=crop_signature,
                )
            )
        return faces

    @staticmethod
    def _encode_face_crop(cv2, image, bbox) -> tuple[Optional[bytes], Optional[int]]:
        """Encode a padded, bounded JPEG crop and a small perceptual signature."""
        x, y, width, height = bbox
        if width <= 0 or height <= 0:
            return None, None

        image_height, image_width = image.shape[:2]
        side = max(width, height) * 1.35
        center_x, center_y = x + width / 2, y + height / 2
        left = max(0, int(center_x - side / 2))
        top = max(0, int(center_y - side / 2))
        right = min(image_width, int(center_x + side / 2))
        bottom = min(image_height, int(center_y + side / 2))
        crop = image[top:bottom, left:right]
        if crop.size == 0:
            return None, None

        longest_side = max(crop.shape[:2])
        if longest_side > 320:
            scale = 320 / longest_side
            crop = cv2.resize(
                crop,
                (max(1, int(crop.shape[1] * scale)), max(1, int(crop.shape[0] * scale))),
                interpolation=cv2.INTER_AREA,
            )

        encoded, jpeg = cv2.imencode(
            ".jpg", crop, [int(cv2.IMWRITE_JPEG_QUALITY), 82]
        )
        if not encoded:
            return None, None

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        thumbnail = cv2.resize(gray, (8, 8), interpolation=cv2.INTER_AREA)
        median = float(thumbnail.mean())
        signature = 0
        for pixel in thumbnail.reshape(-1):
            signature = (signature << 1) | int(float(pixel) >= median)
        return jpeg.tobytes(), signature

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
