"""Start the face-recognition HTTP server on Windows, macOS, or Linux."""
from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SERVER_DIR.parent
ENV_DIR = SERVER_DIR / ".venv"
PYTHON = ENV_DIR / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")


def in_server_environment() -> bool:
    return Path(sys.prefix).resolve() == ENV_DIR.resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Rokid face-recognition server.")
    parser.add_argument("--host", default="0.0.0.0", help="Interface to listen on (default: all interfaces)")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port (default: 8000)")
    parser.add_argument(
        "--threshold", type=float, default=0.363,
        help="SFace cosine-similarity threshold (default: 0.363)",
    )
    args = parser.parse_args()

    if not -1 <= args.threshold <= 1:
        parser.error("--threshold must be between -1 and 1")
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")

    if not in_server_environment():
        if not PYTHON.exists():
            print("Server environment is missing. First run: python server/setup.py", file=sys.stderr)
            return 2
        return subprocess.run(
            [str(PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]],
            cwd=PROJECT_DIR,
            check=False,
        ).returncode

    os.environ["FACE_MATCH_THRESHOLD"] = str(args.threshold)
    sys.path.insert(0, str(PROJECT_DIR))
    import uvicorn

    uvicorn.run("server.app:app", host=args.host, port=args.port, workers=1, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
