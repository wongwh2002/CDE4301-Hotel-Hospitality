"""Create the isolated Python 3.12 environment and fetch OpenCV face models."""
from __future__ import annotations

import platform
import subprocess
import sys
import venv
from pathlib import Path
from urllib.request import Request, urlopen

SERVER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SERVER_DIR.parent
ENV_DIR = SERVER_DIR / ".venv"
PYTHON = ENV_DIR / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")
MODELS = {
    "face_detection_yunet_2023mar.onnx": (
        "https://github.com/opencv/opencv_zoo/raw/refs/heads/main/models/"
        "face_detection_yunet/face_detection_yunet_2023mar.onnx", 100_000,
    ),
    "face_recognition_sface_2021dec.onnx": (
        "https://github.com/opencv/opencv_zoo/raw/refs/heads/main/models/"
        "face_recognition_sface/face_recognition_sface_2021dec.onnx", 1_000_000,
    ),
}


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=PROJECT_DIR, check=True)


def download_models() -> None:
    models_dir = SERVER_DIR / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    for filename, (url, min_size) in MODELS.items():
        destination = models_dir / filename
        if destination.is_file() and destination.stat().st_size >= min_size:
            print(f"Model already present: {destination}", flush=True)
            continue
        temporary = destination.with_suffix(destination.suffix + ".download")
        print(f"Downloading {filename} from OpenCV Zoo...", flush=True)
        request = Request(url, headers={"User-Agent": "Rokid-Face-Prototype/1.0"})
        with urlopen(request, timeout=90) as response, temporary.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        if temporary.stat().st_size < min_size:
            temporary.unlink(missing_ok=True)
            raise RuntimeError(f"Downloaded model is unexpectedly small: {filename}")
        temporary.replace(destination)


def main() -> int:
    if sys.version_info[:2] != (3, 12):
        print("Use Python 3.12 to set up this server.", file=sys.stderr)
        print("Run this script with your Python 3.12 interpreter.", file=sys.stderr)
        return 2

    if not PYTHON.exists():
        print(f"Creating virtual environment: {ENV_DIR}", flush=True)
        venv.EnvBuilder(with_pip=True).create(ENV_DIR)

    run(str(PYTHON), "-m", "pip", "install", "--upgrade", "pip")
    run(str(PYTHON), "-m", "pip", "install", "-r", str(SERVER_DIR / "requirements.txt"))
    download_models()
    print("Setup complete. Add face photos to server/faces/<person name>.<jpg|png>.")
    print("Start the server with: python server/run.py", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
