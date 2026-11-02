"""Create the isolated Python 3.12 environment and cache InsightFace buffalo_l."""
from __future__ import annotations

import platform
import subprocess
import sys
import venv
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SERVER_DIR.parent
ENV_DIR = SERVER_DIR / ".venv"
PYTHON = ENV_DIR / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")
INSIGHTFACE_VERSION = "2.1.0"


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=PROJECT_DIR, check=True)


def download_models() -> None:
    run(str(PYTHON), "-c", (
        "from pathlib import Path; from insightface.app import FaceAnalysis; "
        "root = Path('server/models/insightface').resolve(); "
        "FaceAnalysis(name='buffalo_l', root=str(root), "
        "allowed_modules=['detection', 'recognition'], providers=['CPUExecutionProvider']); "
        "print('buffalo_l cached at', root)"
    ))
    run(str(PYTHON), "-c", (
        "from dotenv import load_dotenv; load_dotenv('server/.env'); "
        "from server.audio_models import WhisperTranscriber; "
        "model = WhisperTranscriber(); model.load(); print('Whisper cached:', model.model_name)"
    ))


def main() -> int:
    if sys.version_info[:2] != (3, 12):
        print("Use Python 3.12 to set up this server.", file=sys.stderr)
        return 2
    if not PYTHON.exists():
        print(f"Creating virtual environment: {ENV_DIR}", flush=True)
        venv.EnvBuilder(with_pip=True).create(ENV_DIR)
    run(str(PYTHON), "-m", "pip", "install", "--upgrade", "pip")
    run(str(PYTHON), "-m", "pip", "install", "-r", str(SERVER_DIR / "requirements.txt"))
    # Same approach as the main face-worker: use headless OpenCV, avoid a second GUI wheel.
    run(str(PYTHON), "-m", "pip", "install", "--no-deps", f"insightface=={INSIGHTFACE_VERSION}")
    download_models()
    print("Setup complete. Add one clear face photo per person to server/faces/.")
    print("Start the server with: python server/run.py", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
