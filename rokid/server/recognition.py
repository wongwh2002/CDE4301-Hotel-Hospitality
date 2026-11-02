"""InsightFace buffalo_l detection and ArcFace matching for the glasses demo."""
from __future__ import annotations

import logging
import math
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

LOG = logging.getLogger("uvicorn.error")
MODEL_NAME = "buffalo_l"
DEFAULT_THRESHOLD = 0.45
DEFAULT_MARGIN = 0.10


@dataclass(frozen=True)
class FaceResult:
    name: str
    similarity: float | None
    box: dict[str, int]
    detection_confidence: float
    runner_up_similarity: float | None = None


def choose_match(scores: dict[str, float], threshold: float, margin: float) -> tuple[str, float | None, float | None]:
    ranked = sorted(((name, score) for name, score in scores.items() if math.isfinite(score)),
                    key=lambda item: item[1], reverse=True)
    if not ranked:
        return "Unknown", None, None
    name, best = ranked[0]
    runner = ranked[1][1] if len(ranked) > 1 else None
    if best < threshold or (runner is not None and best - runner < margin):
        name = "Unknown"
    return name, best, runner


def normalized_embedding(embedding) -> np.ndarray:
    vector = np.asarray(embedding, dtype=np.float32).reshape(-1)
    norm = float(np.linalg.norm(vector))
    if vector.size != 512 or not np.all(np.isfinite(vector)) or not math.isfinite(norm) or norm <= 0:
        raise ValueError("Invalid ArcFace embedding")
    return vector / norm


class InsightFaceRecognizer:
    def __init__(self, threshold: float = DEFAULT_THRESHOLD, margin: float = DEFAULT_MARGIN):
        import onnxruntime as ort
        from insightface.app import FaceAnalysis

        self.threshold = threshold
        self.margin = margin
        server_dir = Path(__file__).parent
        self.model_root = Path(os.getenv("FACE_MODELS_DIR", str(server_dir / "models" / "insightface")))
        options = ort.SessionOptions()
        options.intra_op_num_threads = min(4, os.cpu_count() or 1)
        options.inter_op_num_threads = 1
        self.analysis = FaceAnalysis(name=MODEL_NAME, root=str(self.model_root),
                                     allowed_modules=["detection", "recognition"],
                                     providers=["CPUExecutionProvider"], sess_options=options)
        detection_threshold = float(os.getenv("FACE_DETECTION_CONFIDENCE", "0.5"))
        if not math.isfinite(detection_threshold) or not 0 < detection_threshold <= 1:
            raise ValueError("FACE_DETECTION_CONFIDENCE must be in (0, 1]")
        self.analysis.prepare(ctx_id=0, det_thresh=detection_threshold, det_size=(640, 640))
        self.providers = {name: model.session.get_providers() for name, model in self.analysis.models.items()}
        self.gallery_dir = Path(os.getenv("FACE_GALLERY", str(server_dir / "faces")))
        self.gallery_dir.mkdir(parents=True, exist_ok=True)
        self.gallery: dict[str, list[np.ndarray]] = defaultdict(list)
        self._load_gallery()
        self.analysis.get(np.zeros((320, 320, 3), dtype=np.uint8))

    def _load_gallery(self) -> None:
        supported = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        for path in sorted(self.gallery_dir.iterdir()):
            if not path.is_file() or path.suffix.lower() not in supported:
                continue
            try:
                with Image.open(path) as source:
                    rgb = ImageOps.exif_transpose(source).convert("RGB")
                    image = np.asarray(rgb)[:, :, ::-1].copy()
                faces = self.analysis.get(image)
                if len(faces) != 1:
                    LOG.warning("Skipping reference image: expected one face, detected %d", len(faces))
                    continue
                feature = normalized_embedding(faces[0].embedding)
            except (OSError, ValueError):
                LOG.warning("Skipping unreadable or invalid reference image")
                continue
            self.gallery[path.stem].append(feature)
        LOG.info("Loaded %d face templates for %d names using %s",
                 sum(map(len, self.gallery.values())), len(self.gallery), MODEL_NAME)

    def detect(self, image: np.ndarray) -> list[FaceResult]:
        height, width = image.shape[:2]
        results = []
        for face in self.analysis.get(image):
            x1, y1, x2, y2 = (float(value) for value in face.bbox)
            x1, y1 = max(0, min(width, round(x1))), max(0, min(height, round(y1)))
            x2, y2 = max(x1, min(width, round(x2))), max(y1, min(height, round(y2)))
            if x2 <= x1 or y2 <= y1:
                continue
            try:
                feature = normalized_embedding(face.embedding)
                scores = {name: max(float(np.dot(feature, template)) for template in templates)
                          for name, templates in self.gallery.items()}
                name, best, runner = choose_match(scores, self.threshold, self.margin)
            except ValueError:
                name, best, runner = "Unknown", None, None
            results.append(FaceResult(name, best,
                {"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1},
                float(face.det_score), runner))
        return results
