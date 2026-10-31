#!/usr/bin/env bash
# ==============================================================================
# Hotel Smart-Glasses POC - Local Development Startup Helper
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

# 0. Select an installed Compose v2 CLI. Docker Desktop commonly provides
# `docker compose`; some installations expose the standalone `docker-compose`.
compose_version_supported() {
    local version_output major minor patch
    version_output="$("$@" version 2>&1)" || return 1

    if [[ ! "${version_output}" =~ [vV]?([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
        return 1
    fi

    major="${BASH_REMATCH[1]}"
    minor="${BASH_REMATCH[2]}"
    patch="${BASH_REMATCH[3]}"
    COMPOSE_VERSION="${BASH_REMATCH[0]}"

    if (( major > 2 || (major == 2 && minor > 24) || (major == 2 && minor == 24 && patch >= 4) )); then
        return 0
    fi
    return 1
}

if compose_version_supported docker compose; then
    COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1 && compose_version_supported docker-compose; then
    COMPOSE_CMD=(docker-compose)
else
    echo "ERROR: Docker Compose v2.24.4 or newer was not found." >&2
    echo "Install or update Docker Desktop, or install the Docker Compose v2 plugin." >&2
    echo "Checked both 'docker compose version' and 'docker-compose version'." >&2
    exit 1
fi

echo "==> Using ${COMPOSE_CMD[*]} (${COMPOSE_VERSION})"

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
    is_placeholder = value.strip() in {"replace-with-a-random-secret", "changeme"}
    if separator and key in tokens and (not value.strip() or is_placeholder):
        line = f"{key}={tokens[key]}"
        generated.add(key)
    updated.append(line)
path.write_text("\n".join(updated) + "\n")
path.chmod(0o600)
if generated:
    print("==> Generated missing local token(s); .env is excluded from Git.")
PY

echo "==> HOST_BIND_ADDRESS defaults to 127.0.0.1. Set it to the laptop's private LAN IP for phone testing."

# 2. Derive default project name if not already set in environment
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-hotel-poc}"

echo "===================================================================="
echo " Starting Hotel Smart-Glasses POC Stack (Project: ${PROJECT_NAME})"
echo "===================================================================="
echo " Core services starting by default:"
echo "   - lounge-control  (FastAPI orchestrator, device WebSocket hub)"
echo "   - face-worker     (CPU face detection and active-cohort matching)"
echo "   - mock-hotel      (Synthetic SQLite guest profiles)"
echo ""
echo " Note: Tap simulator and frame replay are opt-in under 'sim' profile."
echo "===================================================================="

# 3. Launch Docker Compose with passed arguments or default up --build --wait
if [[ $# -eq 0 ]]; then
    "${COMPOSE_CMD[@]}" -p "${PROJECT_NAME}" up --build --wait
else
    "${COMPOSE_CMD[@]}" -p "${PROJECT_NAME}" "$@"
fi

echo ""
echo "===================================================================="
echo " Stack is healthy and ready!"
echo "===================================================================="
echo " Published endpoints use HOST_BIND_ADDRESS from .env (127.0.0.1 by default):"
echo "   - lounge-control: http://<HOST_BIND_ADDRESS>:8000"
echo "     Health:         http://<HOST_BIND_ADDRESS>:8000/health"
echo "     Active Cohort:  http://<HOST_BIND_ADDRESS>:8000/v1/lounge/cohort"
echo "     Video WebSocket: ws://<HOST_BIND_ADDRESS>:8003/v1/video/stream/{device_id}"
echo "     Device WebSocket: ws://<HOST_BIND_ADDRESS>:8000/v1/devices/{device_id}/stream"
echo "   - face-worker:    http://<HOST_BIND_ADDRESS>:8001/health"
echo "   - mock-hotel:     http://<HOST_BIND_ADDRESS>:8002/health"
echo ""
echo " Useful commands:"
echo "   - Start with tap simulator:"
echo "       ${COMPOSE_CMD[*]} -p ${PROJECT_NAME} --profile sim up --build --wait lounge-control face-worker mock-hotel tap-simulator"
echo "   - Run one-shot frame replay fixture:"
echo "       ${COMPOSE_CMD[*]} -p ${PROJECT_NAME} --profile sim run --rm frame-replay"
echo "   - View logs:"
echo "       ${COMPOSE_CMD[*]} -p ${PROJECT_NAME} logs -f"
echo "   - Stop stack:"
echo "       ${COMPOSE_CMD[*]} -p ${PROJECT_NAME} down"
echo "===================================================================="
