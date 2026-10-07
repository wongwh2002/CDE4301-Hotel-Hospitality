#!/usr/bin/env bash
# ==============================================================================
# Hotel Smart-Glasses POC - Local Development Startup Helper
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

# 1. Initialize .env from .env.example if missing
if [[ ! -f ".env" ]]; then
    echo "==> Creating .env from .env.example..."
    cp .env.example .env
fi

python3 - <<'PY'
from pathlib import Path
import secrets

path = Path(".env")
lines = path.read_text().splitlines()
tokens = {
    "DEVICE_AUTH_TOKEN": secrets.token_urlsafe(32),
    "INTERNAL_API_TOKEN": secrets.token_urlsafe(32),
}
generated = set()
updated = []
for line in lines:
    key, separator, value = line.partition("=")
    if separator and key in tokens and not value.strip():
        line = f"{key}={tokens[key]}"
        generated.add(key)
    updated.append(line)
path.write_text("\n".join(updated) + "\n")
path.chmod(0o600)
if generated:
    print("==> Generated local device and service tokens; .env is excluded from Git.")
PY

echo "==> HOST_BIND_ADDRESS defaults to 127.0.0.1. Set it to the laptop's private LAN IP for phone testing."

# 2. Derive default project name if not already set in environment
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-hotel-poc}"

echo "===================================================================="
echo " Starting Hotel Smart-Glasses POC Stack (Project: ${PROJECT_NAME})"
echo "===================================================================="
echo " Core services starting by default:"
echo "   - lounge-control  (FastAPI orchestrator, device WebSocket hub)"
echo "   - face-worker     (Transient bounded CV skeleton)"
echo "   - mock-hotel      (Synthetic SQLite guest profiles)"
echo ""
echo " Note: Tap simulator and frame replay are opt-in under 'sim' profile."
echo "===================================================================="

# 3. Launch Docker Compose with passed arguments or default up --build --wait
if [[ $# -eq 0 ]]; then
    docker compose -p "${PROJECT_NAME}" up --build --wait
else
    docker compose -p "${PROJECT_NAME}" "$@"
fi

echo ""
echo "===================================================================="
echo " Stack is healthy and ready!"
echo "===================================================================="
echo " Published endpoints use HOST_BIND_ADDRESS from .env (127.0.0.1 by default):"
echo "   - lounge-control: http://<HOST_BIND_ADDRESS>:8000"
echo "     Health:         http://<HOST_BIND_ADDRESS>:8000/health"
echo "     Active Cohort:  http://<HOST_BIND_ADDRESS>:8000/v1/lounge/cohort"
echo "     WebSocket:      ws://<HOST_BIND_ADDRESS>:8000/v1/devices/{device_id}/stream"
echo "   - face-worker:    http://<HOST_BIND_ADDRESS>:8001/health"
echo "   - mock-hotel:     http://<HOST_BIND_ADDRESS>:8002/health"
echo ""
echo " Useful commands:"
echo "   - Start with tap simulator:"
echo "       docker compose -p ${PROJECT_NAME} --profile sim up --build --wait lounge-control face-worker mock-hotel tap-simulator"
echo "   - Run one-shot frame replay fixture:"
echo "       docker compose -p ${PROJECT_NAME} --profile sim run --rm frame-replay"
echo "   - View logs:"
echo "       docker compose -p ${PROJECT_NAME} logs -f"
echo "   - Stop stack:"
echo "       docker compose -p ${PROJECT_NAME} down"
echo "===================================================================="
