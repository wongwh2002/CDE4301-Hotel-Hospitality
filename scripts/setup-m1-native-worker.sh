#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT_DIR}"

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "This setup is for Apple Silicon macOS (Darwin arm64)." >&2
  exit 1
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"
"${PYTHON_BIN}" -m venv .venv-m1
"${ROOT_DIR}/.venv-m1/bin/python" -m pip install --upgrade pip
"${ROOT_DIR}/.venv-m1/bin/python" -m pip install -r apps/face-worker/requirements.txt
"${ROOT_DIR}/.venv-m1/bin/python" -m pip install --no-deps insightface==2.1.0
"${ROOT_DIR}/.venv-m1/bin/python" - <<'PY'
import platform
import onnxruntime

print(f"Python architecture: {platform.machine()}")
print(f"ONNX Runtime: {onnxruntime.__version__}")
print(f"Execution providers: {', '.join(onnxruntime.get_available_providers())}")
if "CoreMLExecutionProvider" not in onnxruntime.get_available_providers():
    raise SystemExit(
        "This ONNX Runtime install has no CoreMLExecutionProvider. "
        "Use FACE_EXECUTION_PROVIDER=cpu or resolve the wheel/platform mismatch."
    )
PY
