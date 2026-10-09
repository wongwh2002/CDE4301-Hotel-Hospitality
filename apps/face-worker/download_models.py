"""Download the pinned OpenCV Zoo face models into a local model cache."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import urllib.request


MODELS = {
    "yunet.onnx": {
        "url": (
            "https://huggingface.co/opencv/opencv_zoo/resolve/main/"
            "models/face_detection_yunet/face_detection_yunet_2023mar.onnx?download=true"
        ),
        "sha256": "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4",
    },
    "sface.onnx": {
        "url": (
            "https://huggingface.co/opencv/opencv_zoo/resolve/main/"
            "models/face_recognition_sface/face_recognition_sface_2021dec.onnx?download=true"
        ),
        "sha256": "0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79",
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as model_file:
        for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_models(model_dir: str | Path) -> dict[str, Path]:
    """Fetch missing model files, rejecting bytes that fail the pinned digest."""
    target_dir = Path(model_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, Path] = {}

    for filename, spec in MODELS.items():
        target = target_dir / filename
        if target.exists() and _sha256(target) == spec["sha256"]:
            results[filename] = target
            continue

        temporary = target.with_name(f".{filename}.download")
        request = urllib.request.Request(
            spec["url"], headers={"User-Agent": "hotel-lounge-poc/face-worker"}
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                with temporary.open("wb") as output:
                    while chunk := response.read(1024 * 1024):
                        output.write(chunk)
            actual = _sha256(temporary)
            if actual != spec["sha256"]:
                raise RuntimeError(
                    f"SHA-256 mismatch for {filename}: expected {spec['sha256']}, got {actual}"
                )
            os.replace(temporary, target)
            results[filename] = target
        finally:
            temporary.unlink(missing_ok=True)

    return results
