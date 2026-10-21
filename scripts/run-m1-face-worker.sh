#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT_DIR}"

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "This worker launcher is for Apple Silicon macOS (Darwin arm64)." >&2
  exit 1
fi
if [[ ! -x .venv-m1/bin/uvicorn ]]; then
  echo "Run scripts/setup-m1-native-worker.sh first." >&2
  exit 1
fi
if [[ -z "${INTERNAL_API_TOKEN:-}" ]]; then
  echo "Load INTERNAL_API_TOKEN from your local .env before starting the worker." >&2
  exit 1
fi

export FACE_RECOGNITION_ENABLED=true
export FACE_EXECUTION_PROVIDER="${FACE_EXECUTION_PROVIDER:-coreml}"
export COREML_COMPUTE_UNITS="${COREML_COMPUTE_UNITS:-CPUAndGPU}"
export COREML_PROFILE_COMPUTE_PLAN="${COREML_PROFILE_COMPUTE_PLAN:-false}"
export FACE_MODELS_DIR="${FACE_MODELS_DIR:-${HOME}/.insightface}"
export LOUNGE_CONTROL_URL="${LOUNGE_CONTROL_URL:-http://127.0.0.1:18100}"
export PORT="${NATIVE_FACE_WORKER_PORT:-18101}"

exec .venv-m1/bin/uvicorn main:app \
  --app-dir apps/face-worker \
  --host "${NATIVE_FACE_WORKER_HOST:-0.0.0.0}" \
  --port "${PORT}"
