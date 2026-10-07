# CDE4301-Hotel-Hospitality-

## Hotel smart-glasses POC

After enabling GitHub Pages from the `main` branch's `/docs` folder, open the interactive architecture diagram here:

- [Open the architecture page](https://wongwh2002.github.io/CDE4301-Hotel-Hospitality/architecture/hotel-lounge-smart-glasses-poc.html)
- [View the HTML source](docs/architecture/hotel-lounge-smart-glasses-poc.html)
- [Read the architecture proposal](docs/architecture/hotel-lounge-smart-glasses-poc.md)

---

### Scaffold Status

> [!NOTE]
> This repository provides a **runnable development scaffold** implementing the proposed architecture in [the architecture proposal](docs/architecture/hotel-lounge-smart-glasses-poc.md). The architecture is currently a proposal. This implementation serves as an integration skeleton and **does not claim real face recognition or validated Rokid camera streaming**. Live camera delivery on Rokid RV101 remains an unresolved validation gate.

### Architecture Overview

```
Docker Compose
├── lounge-control (port 8000)
│   ├── Card tap ingestion (POST /v1/lounge/taps, idempotent)
│   ├── In-memory active lounge cohort (TTL expiry, zero image persistence)
│   ├── Multi-device authenticated WebSocket hub (/v1/devices/{device_id}/stream)
│   └── Compact glanceable cue composer (🟢 ✅ ALEX / 🔴 ⚠️ PEANUT ALLERGY)
├── face-worker (port 8001)
│   ├── Candidate enrollment (PUT /internal/v1/candidates/{id}, RAM only, photo discarded)
│   ├── Frame intake & validation (POST /internal/v1/frames, binary JPEG, bounds check)
│   ├── Bounded per-stream queue (drops oldest frames to avoid latency buildup)
│   └── Validation skeleton only (strictly does not fabricate matches)
└── mock-hotel (port 8002)
    ├── SQLite database on named volume (mock-hotel-data)
    └── Seeded clearly synthetic guest profiles and synthetic reference photos

Opt-in Simulators (under 'sim' profile)
├── tap-simulator: Simulates card-reader entry and exit tap events
└── frame-replay: One-shot deterministic replay of a synthetic JPEG fixture over WebSocket
```

### Shared Contracts

Versioned contracts and JSON schemas live in [`contracts/`](contracts/):
- `tap-event.schema.json`: Access controller card-reader tap events.
- `device-stream.schema.json`: WebSocket frame metadata and messages.
- `match-event.schema.json`: Internal face matching event (strictly opaque candidate IDs, zero PII).
- `cue.schema.json`: Glanceable cue display message delivered to companion phones.
- `lounge-profile.schema.json`: Minimal permitted guest profile.
- `candidate.schema.json`: In-memory candidate enrollment payload.

Shared Pydantic models are defined in [`contracts/models.py`](contracts/models.py).

---

### Quickstart

#### 1. Setup Environment Configuration

On first run, `./scripts/dev-up.sh` creates a private `.env` file and generates unique device and internal service tokens. To configure Compose manually, copy `.env.example` to `.env`, set both tokens, and then start the stack.

```bash
cp .env.example .env
# Set DEVICE_AUTH_TOKEN and INTERNAL_API_TOKEN to unique random values.
```

#### 2. Start Core Stack

Using the development helper script:

```bash
./scripts/dev-up.sh
```

Or using Docker Compose directly:

```bash
docker compose up --build --wait
```

The three core services (`lounge-control`, `face-worker`, `mock-hotel`) start and await healthcheck readiness before completing startup.

#### 3. Verify Health

- `lounge-control`: `curl http://127.0.0.1:8000/health`
- `face-worker`: `curl http://127.0.0.1:8001/health`
- `mock-hotel`: `curl http://127.0.0.1:8002/health`
- Active cohort: `curl http://127.0.0.1:8000/v1/lounge/cohort`

---

### Networking & Private LAN Configuration

> [!CAUTION]
> **Private-LAN-Only Requirement:**
> This stack is intended strictly for local development or on a dedicated, trusted private router or phone hotspot.
> **DO NOT** expose this stack to the public internet or configure router port forwarding.

All three core service ports are published on the laptop host so companion phones or simulators on the same trusted Wi-Fi network can communicate with the laptop.

- **Local testing:** Leave `HOST_BIND_ADDRESS=127.0.0.1` in `.env`.
- **Physical phone testing:** Set `HOST_BIND_ADDRESS` in `.env` to your laptop's private LAN IP (e.g., `192.168.1.50`). Companion phone apps connect to `http://<laptop-lan-ip>:8000` and `ws://<laptop-lan-ip>:8000`.

---

### Device WebSocket Authentication & Session Management

Each paired phone companion app connects to:

```text
ws://<HOST_BIND_ADDRESS>:8000/v1/devices/{device_id}/stream?token=<DEVICE_AUTH_TOKEN>
```

- **Authentication:** Token credentials are configured via `DEVICE_AUTH_TOKEN` in `.env` (never hardcoded in source). Authentication is verified on connection; unauthorized connections are rejected with WebSocket close code `1008` (Policy Violation).
- **Service authentication:** Internal face-worker routes require the separate `INTERNAL_API_TOKEN`. Compose passes it between services in an HTTP header; phone clients do not use it.
- **Multi-Phone Support:** A single `lounge-control` container manages multiple concurrent phone WebSockets, keeping sessions, stream mappings, and frame metadata distinct per device.
- **Disconnect Cleanup:** Disconnected devices are automatically deregistered, clearing active stream associations and preventing stale cue delivery.
- **Transient Frames:** Incoming binary frames are forwarded immediately via internal HTTP to `face-worker` and discarded. Neither `lounge-control` nor `face-worker` persists camera frames or crops to disk.

---

### Simulators & Replay Workflows

The `sim` profile includes `tap-simulator` and `frame-replay`.

#### Running Core Services with Tap Simulator

Start the stack with continuous simulated card-reader taps:

```bash
docker compose --profile sim up --build --wait lounge-control face-worker mock-hotel tap-simulator
```

#### One-Shot Frame Replay

Run a one-shot replay of a prepared synthetic JPEG fixture through the real device WebSocket interface:

```bash
docker compose --profile sim run --rm frame-replay
```

To specify custom options or a custom fixture:

```bash
docker compose --profile sim run --rm frame-replay --fixture /path/to/consented_frame.jpg --frames 5
```

The replay client connects, transmits the frame fixture, logs transmission metrics (without logging frame payloads), listens for cues, and cleanly exits.

---

### Running Automated Checks

To run the automated tests outside of AGY:

```bash
python3 -m pip install -r requirements-test.txt
python3 -m pytest
```
