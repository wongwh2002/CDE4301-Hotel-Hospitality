# CDE4301-Hotel-Hospitality-

## Hotel smart-glasses POC

After enabling GitHub Pages from the `main` branch's `/docs` folder, open the interactive architecture diagram here:

- [Open the architecture page](https://wongwh2002.github.io/CDE4301-Hotel-Hospitality/architecture/hotel-lounge-smart-glasses-poc.html)
- [View the HTML source](docs/architecture/hotel-lounge-smart-glasses-poc.html)
- [Read the architecture proposal](docs/architecture/hotel-lounge-smart-glasses-poc.md)

For the project problem framing and personalization evidence:

- [Open the hotel personalization learning map](https://wongwh2002.github.io/CDE4301-Hotel-Hospitality/research/hotel-personalization-learning-map.html)
- [View the HTML source](docs/research/hotel-personalization-learning-map.html)
- [Read the additional luxury and business-traveler evidence](docs/research/hotel-personalization-additional-evidence.md)

---

### Scaffold Status

> [!NOTE]
> This repository provides a runnable local POC for the proposed architecture in [the architecture proposal](docs/architecture/hotel-lounge-smart-glasses-poc.md). The face worker runs real CPU face detection and matching against the active mock-hotel cohort, but the demo uses synthetic data and does not establish real-world accuracy, safety, or performance. Live camera delivery on Rokid RV101 remains an unresolved validation gate.

### Architecture Overview

```
Docker Compose
├── lounge-control (ports 8000 and 8003)
│   ├── Card tap ingestion (POST /v1/lounge/taps, idempotent)
│   ├── In-memory active lounge cohort (TTL expiry, zero image persistence)
│   ├── Multi-device authenticated WebSocket hub (/v1/devices/{device_id}/stream)
│   ├── Video-stream alias (/v1/video/stream/{device_id}) with aggregate detection sets
│   ├── Laptop dashboard (guest registration, entry/exit taps, live roster)
│   └── Compact glanceable cue composer (🟢 ✅ ALEX / 🔴 ⚠️ PEANUT ALLERGY)
├── face-worker (port 8001)
│   ├── Candidate enrollment (PUT /internal/v1/candidates/{id}, RAM only, photo discarded)
│   ├── Frame intake & validation (POST /internal/v1/frames, binary JPEG, bounds check)
│   ├── Per-stream freshest-frame processing (drops stale and out-of-order frames)
│   └── CPU face detection and active-cohort matching with buffalo_l
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
- `detection-set.schema.json`: Full snapshot of stable, identified guests currently detected in one stream.
- `lounge-profile.schema.json`: Minimal permitted guest profile.
- `candidate.schema.json`: In-memory candidate enrollment payload.

Shared Pydantic models are defined in [`contracts/models.py`](contracts/models.py).

---

### Quickstart

#### 1. Setup Environment Configuration

On first run, `./scripts/dev-up.sh` creates a private `.env` file with the POC device token set to `gedi-4301` and generates a separate random `INTERNAL_API_TOKEN`. The dashboard loads the configured `DEVICE_AUTH_TOKEN` automatically, so staff do not need to type it into the face test. To configure Compose manually, copy `.env.example` to `.env` and generate an `INTERNAL_API_TOKEN`. Keep `.env` private; it is excluded from Git.

```bash
cp .env.example .env
openssl rand -hex 32
# Put the output into INTERNAL_API_TOKEN in .env.
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

The three core services (`lounge-control`, `face-worker`, `mock-hotel`) start and await healthcheck readiness before Compose returns. Host ports `8000` and `8003` both map to the same `lounge-control` container (container port `8000`); port `8003` is a convenient video-stream address, not another container. `lounge-control` forwards frames internally to `face-worker`.
On first startup, `face-worker` downloads the InsightFace `buffalo_l` model pack into the `face-model-cache` Compose volume. This one-time download needs internet access. Alex's seeded profile uses a fictional, generated test face so the optional frame replay can exercise a local stable match; other seeded profiles keep person-free placeholder images. See the [mobile-friendly architecture and demo guide](docs/architecture/face-recognition-demo.md) and [`apps/face-worker/MODELS.md`](apps/face-worker/MODELS.md) for more detail.

#### 3. Open the Laptop Dashboard

Open `http://127.0.0.1:8000/` on the laptop. The dashboard starts with a seeded guest selected, lets you edit the guest reference, register mock guests with up to three uploaded or camera-captured face photos, edit an existing guest's profile and saved photos, send entry/exit taps, and view the active roster. In edit mode, saved photos are shown; selecting new photos replaces the full saved set, while leaving the selection empty keeps it. If you change an already admitted guest's photos or profile fields, depart and admit them again to refresh the active face-worker candidate. For phone or other laptop access on the trusted Wi-Fi, use `http://<laptop-lan-ip>:8000/` after setting `HOST_BIND_ADDRESS` as described below. The local mock-hotel SQLite volume retains reference photos for re-enrollment; use synthetic or consented demo images.

#### 4. Verify Health

- `lounge-control`: `curl http://127.0.0.1:8000/health`
- `face-worker`: `curl http://127.0.0.1:8001/health`
- `mock-hotel`: `curl http://127.0.0.1:8002/health`
- Active cohort: `curl http://127.0.0.1:8000/v1/lounge/cohort`

`lounge-control` keeps a guest present even if face-worker enrollment is temporarily unavailable. The tap response and dashboard show `recognition_status`: `ready` or `ready_partial` means at least one reference photo produced a template; `enrollment_pending` means the profile is in the roster while enrollment awaits retry; `no_reference_photos` and `no_single_face` mean the saved images need correcting; `recognition_disabled` means the model is unavailable; and `enrollment_failed` means the worker rejected the request. For missing or invalid reference photos, edit the guest photos and depart/admit again. Lounge-control retries dependency failures and restores active templates from mock-hotel photos after a face-worker restart. The lounge-control health response includes `recognition_pending_candidates`.

---

### Networking & Private LAN Configuration

> [!CAUTION]
> **Private-LAN-Only Requirement:**
> This stack is intended strictly for local development or on a dedicated, trusted private router or phone hotspot.
> **DO NOT** expose this stack to the public internet or configure router port forwarding.

The core service ports and the video-stream port are published on the laptop host so companion phones or simulators on the same trusted Wi-Fi network can communicate with it.

- **Local testing:** Leave `HOST_BIND_ADDRESS=127.0.0.1` in `.env` and open `http://localhost:8000/` on the laptop.
- **Physical phone testing:** Connect the laptop and phone to the same private router or phone hotspot. Find the laptop's Wi-Fi IPv4 address (macOS: `ipconfig getifaddr en0`; Windows: `ipconfig`; Linux: `ip -4 addr`), then set `HOST_BIND_ADDRESS` in `.env` to that private address, such as `192.168.1.50`. This binds the services to the LAN address, so use `http://<laptop-lan-ip>:8000/` on the phone and `http://<laptop-lan-ip>:8000/` or `http://localhost:8000/` on the laptop if you also enable the local override below. Re-run the same Compose startup command after changing `.env`. If the phone cannot connect, check that both devices joined the same Wi-Fi and that the laptop firewall allows these ports; some hotspots enable client isolation.
- **Both localhost and LAN:** With `HOST_BIND_ADDRESS` set to the laptop's private IP, add `COMPOSE_FILE=compose.yaml:compose.loopback.yaml` to `.env`. This adds `127.0.0.1` bindings for lounge-control's ports 8000 and 8003 while preserving their LAN bindings. Restart the stack with the same launcher you used before. Remove the `COMPOSE_FILE` line to return to LAN-only bindings.
- Phones use the laptop's LAN address; `127.0.0.1` on a phone points back to the phone itself. The phone sends frames to lounge-control on `8003`; the dashboard uses `8000`. Ports `8001` and `8002` are development/health endpoints and are not part of the phone data flow.

Browsers permit camera access from an HTTP page on `localhost` because it is a secure context. A browser on another device cannot use the laptop's `localhost`; accessing the dashboard by its LAN IP over HTTP does not grant camera access. The other device needs a trusted HTTPS setup or a companion app.

---

### Device WebSocket Authentication & Session Management

Each paired phone companion app opens one authenticated WebSocket per phone. Use a unique `device_id` for each phone; only one connection for a given `device_id` can be active at a time. For video upload, connect to:

```text
ws://<laptop-lan-ip>:8003/v1/video/stream/<device_id>
WebSocket subprotocols: device-stream-v1, device-token.<DEVICE_AUTH_TOKEN>
```

Port `8003` is another published port for the existing `lounge-control` container, not a separate service. The compatibility route `ws://<laptop-lan-ip>:8000/v1/devices/<device_id>/stream` reaches the same handler and service.

- **Authentication:** The POC default is `gedi-4301`, configured as `DEVICE_AUTH_TOKEN` in `.env`. The dashboard preloads the configured value. Phone clients read the token from `.env` and send it as the `device-token.<DEVICE_AUTH_TOKEN>` WebSocket subprotocol; unauthorized connections are rejected with WebSocket close code `1008` (Policy Violation).
- **Service authentication:** Internal face-worker routes require the separate `INTERNAL_API_TOKEN`. Compose passes it between services in an HTTP header; phone clients do not use it.
- **Multi-Phone Support:** A single `lounge-control` container manages multiple concurrent phone WebSockets, keeping sessions, stream mappings, and frame metadata distinct per device.
- **Disconnect Cleanup:** Disconnected devices are automatically deregistered, clearing active stream associations and preventing stale cue delivery.
- **Transient Frames:** Incoming binary frames are forwarded immediately via internal HTTP to `face-worker` and discarded. Neither `lounge-control` nor `face-worker` persists camera frames or crops to disk.

#### Image and embedding storage

- Guest reference images are JPEG BLOBs in the mock-hotel SQLite database: one primary image on the `guests` row and up to two additional rows in `guest_reference_photos`. The database lives in the Compose `mock-hotel-data` volume, so reference photos survive container restarts and are removed by `docker compose down -v`.
- Camera frames and generated face crops are transient. They pass through service memory and WebSocket messages and are not written to the database or Docker logs.
- Face-worker derives normalized 512-value embeddings from admitted guests' reference photos. Those vectors stay in the worker's RAM while each guest is an active candidate, then are removed on departure, expiry, or restart. There is no vector database or on-disk embedding index in this POC.

#### Opt-in raw face debug view

Set `debug_faces: true` in a `frame_meta` message to receive every face detection produced by the detector, including detections whose identity similarity is below the guest-match threshold. The dashboard's **Face Recognition Test** enables this automatically and displays each transient face crop, track ID, detector score, best identity similarity, candidate-threshold result, and timing summary.

The phone receives `debug_timing` after frame handoff from lounge-control, then a `debug_frame` callback with worker queue-wait, detection, tracking/matching, and total processing times. To inspect score/box summaries in Docker, run:

```bash
docker compose -p hotel-poc logs -f lounge-control face-worker
```

Logs contain detector boxes, scores, crop IDs, and timing values; they never contain JPEG bytes. “All detections” means all faces returned by the model's configured detector. The identity matching threshold does not filter this debug view.

For verbose face-worker progress, set `FACE_WORKER_LOG_LEVEL=DEBUG` in `.env`, then rebuild and recreate the service with `docker compose -p hotel-poc up -d --build --force-recreate face-worker`. Follow the logs with:

```bash
docker compose -p hotel-poc logs -f --tail=200 face-worker lounge-control
```

At `DEBUG`, face-worker logs frame queueing and dequeue, detector start/completion, per-face best-candidate score and rejection reason, the rolling stability votes, and match-callback results. At `INFO`, it logs model startup, candidate enrollment/removal, stable-match/clear callbacks, queue drops, and the existing opt-in raw-detection summaries. These logs use opaque candidate and track IDs; guest names, embeddings, JPEG frames, and face crops are not logged.

Frame freshness defaults are `MAX_FRAME_AGE_SECONDS=2.0` and `MAX_FRAME_QUEUE_AGE_SECONDS=1.0`. A parseable ISO-8601 `captured_at` older than two seconds is rejected at intake and checked again immediately before inference; frames that wait over one second in the worker queue are dropped before inference. Each stream must use increasing sequence numbers; duplicate or older sequences are rejected. When inference falls behind, the worker selects the newest queued frame and discards older queued frames. Keep phone and laptop clocks synchronized for capture-time rejection; if `captured_at` is absent or unparseable, the worker still applies the local queue-age and sequence checks. Tune these defaults only after measuring capture-to-cue delay on the target phone and laptop. With `debug_faces: true`, the timing row also shows whether the worker accepted or dropped a frame; stale and out-of-order reasons are logged by face-worker.

The worker response looks like this; `crop_b64` carries the transient JPEG bytes:

```json
{
  "type": "debug_frame",
  "device_id": "rv101-phone-01",
  "stream_id": "lounge-session-001",
  "sequence": 1,
  "captured_at": "2026-10-10T15:00:00.123+08:00",
  "queue_wait_ms": 0.4,
  "detect_ms": 81.2,
  "association_ms": 1.1,
  "processing_ms": 82.7,
  "faces": [{
    "track_id": "track-a81b2c3d4e5f",
    "bbox": [120, 45, 88, 104],
    "detector_score": 0.42,
    "match_score": 0.31,
    "candidate_match": false,
    "crop_id": "debug-0123456789abcdef01234567",
    "crop_b64": "/9j/2Q=="
  }]
}
```

### Phone Camera Bridge: Detect, Upload, Display

The phone app is the bridge between the glasses camera/display and the laptop. For the first POC, run a small **face-presence trigger on the paired phone** when the glasses SDK exposes preview frames. Keep identity matching on the laptop in `face-worker`; the phone detector only decides whether a frame should be uploaded. Meta's toolkit connects a phone app to compatible glasses. For the physical Rokid RV101, the CXR-L sample currently documented in this repo demonstrates still-photo capture, but does not prove a continuous preview stream or custom model execution on the glasses. Treat that camera capability as a device-validation gate. ([Meta Device Access Toolkit](https://developers.meta.com/wearables/device-access-toolkit/), [RV101 CXR-L photo sample](https://github.com/e7naq3y/CXR-L-SDK/blob/main/cxrlsample101/app/src/main/java/com/rokid/cxrlsample/activities/photo/PhotoUsageViewModel.kt))

The phone sends JPEG frame messages to `lounge-control` over the WebSocket on host port `8003`. The same endpoint supports these capture patterns:

- **One still image:** connect, send one `frame_meta` message followed by its binary JPEG, wait for a response or timeout, then close. The frame is accepted, but one image cannot fill the default three-observation window; a guest is returned after the same candidate passes in at least two of those three observations.
- **Short burst:** open one WebSocket for a capture event, send three distinct frames with increasing sequence numbers and the same `stream_id`, wait for the match result or timeout, then close. That brief connect-send-wait-close cycle is what “one short connection” means; you do not keep it open between capture events.
- **Ongoing sampled feed:** keep the WebSocket open during the camera session and send repeated `frame_meta`/JPEG pairs. Start around 1 frame per second on the current laptop Docker setup; higher rates may queue or drop frames depending on inference speed. This behaves like a live feed made from still frames.

Each frame is sent separately; this endpoint does not accept raw RTSP or H.264 video. Lounge-control forwards frames to `face-worker`. The repo contains the server endpoint and a replay client, but does not yet include an Android companion app that captures from the glasses and sends frames.

#### Recommended capture flow

1. Connect the glasses to the companion phone using the vendor SDK. If the SDK supplies a live preview, run a lightweight face detector on downscaled preview frames on the phone. Do not assume the detector runs on the glasses themselves.
2. When the detector first sees a face, send a short burst of **three distinct frames** to the laptop, then apply a cooldown until the face leaves or the trigger resets. The worker confirms an identity when the same guest passes matching checks in at least two of the three observations. Do not resend the same JPEG three times as if they were independent observations.
3. Send the full scene JPEG for each selected frame. The laptop worker detects and tracks every visible face, then matches only against currently active lounge candidates. The phone does not send guest names, allergies, card numbers, or a claimed identity. The face-presence result stays local and is not part of the current wire contract.
4. `lounge-control` forwards each transient JPEG to `face-worker`. Stable matches return on the same WebSocket as a full per-person snapshot, separate cropped-face messages, and the existing per-track cue/clear updates; the phone joins the person and image data and renders it through the glasses SDK.

If the SDK only provides still-photo capture, there is no preview frame on which to run a pre-capture trigger. You can run the detector on each requested photo and upload only photos containing a face, but that filters network traffic after capture; it does not trigger the shutter. A single still also cannot fill the current three-observation confirmation window. Validate continuous preview or a burst of distinct photos on the exact glasses/SDK before promising automatic detection-triggered cues.

#### WebSocket frame format

Pass `device-stream-v1` and `device-token.<DEVICE_AUTH_TOKEN>` (with the actual local token value) as WebSocket subprotocols. Do not put the token in the URL. The server selects `device-stream-v1` for the connection; the token subprotocol is used only to authenticate it. `INTERNAL_API_TOKEN` is a separate service-to-service credential and must not be sent by the phone.

After the server replies with `session_ack`, send this JSON text message immediately before each frame's binary JPEG message:

```json
{
  "type": "frame_meta",
  "device_id": "rv101-phone-01",
  "stream_id": "lounge-session-001",
  "sequence": 1,
  "captured_at": "2026-10-10T15:00:00.123+08:00",
  "format": "image/jpeg",
  "debug_faces": true
}
```

Then send the JPEG bytes as a **WebSocket binary message**, not as base64 JSON. Send each metadata/binary pair back-to-back before sending the next frame's metadata. Increment `sequence` for every frame on that stream and use that frame's capture time. Keep each image below `MAX_FRAME_SIZE_BYTES` (5 MiB by default). The `device_id` in metadata is optional; if included, it must match the ID in the WebSocket path. `debug_faces` is optional and defaults to `false`; use `true` only while diagnosing detection. See [`contracts/device-stream.schema.json`](contracts/device-stream.schema.json).

The phone should listen for JSON messages on this same connection. An active cue has `type: "cue"`, `status: "active"`, and a nested `cue` object containing `headline` plus an optional `alert`; a clear/suppressed cue uses `type: "clear"`. See [`contracts/cue.schema.json`](contracts/cue.schema.json). Do not let a cue from an old `stream_id` remain displayed after disconnect or session change.

#### Detection-set response

After the first `frame_meta` message for a stream, the server sends an initial empty snapshot. Lounge-control sends a full `detection_set` when the set changes and then once per second while the stream is connected. Each snapshot contains all currently stable, identified tracks; two people with the same name remain separate because each entry has its own `track_id`. Unknown and unconfirmed faces are excluded. Existing per-track `cue` and `clear` messages remain available.

```json
{
  "type": "detection_set",
  "stream_id": "lounge-session-001",
  "people": [
    {
      "track_id": "track-a81b2c3d4e5f",
      "guest_id": "guest-a81b2c3d4e5f0123456789abcd",
      "display_name": "ALEX",
      "confidence": 0.82,
      "preferences": ["Sparkling water"],
      "allergies": ["Peanut allergy"],
      "crop_id": "crop-0123456789abcdef01234567",
      "alert": "🔴 ⚠️ 🥜 PEANUT ALLERGY"
    },
    {
      "track_id": "track-0123456789ab",
      "guest_id": "guest-0123456789abcdef0123456789ab",
      "display_name": "JORDAN",
      "confidence": 0.74,
      "preferences": [],
      "allergies": [],
      "crop_id": "crop-89abcdef0123456701234567"
    }
  ],
  "emitted_at": "2026-10-15T09:00:00+00:00"
}
```

Each item in `people` is the per-person dictionary the phone can display. `confidence` is the face embedding cosine-similarity score from 0 to 1, not a calibrated probability. The wire protocol sends the profile fields in `detection_set` and the cropped JPEG in a separate `face_crop` message; the phone joins them by `crop_id` and keeps one display card per `track_id`. For example, a phone-side card can be assembled as:

```json
{
  "guest_id": "guest-a81b2c3d4e5f0123456789abcd",
  "display_name": "ALEX",
  "confidence": 0.82,
  "track_id": "track-a81b2c3d4e5f",
  "cropped_face": "<JPEG cached using crop_id>",
  "preferences": ["Sparkling water"],
  "allergies": ["Peanut allergy"]
}
```

This is the client-side display object, not a third WebSocket message. Keep cards keyed by `track_id`, not by name, so two people with the same name stay separate. `guest_id` identifies the guest profile, while `track_id` identifies the temporary face track.

Every stable person entry includes `crop_id`. Lounge-control sends the cropped JPEG separately over the same WebSocket as a `face_crop` JSON message before publishing a snapshot that refers to that crop. A new crop is sent when a track first becomes stable or its face crop materially changes:

```json
{
  "type": "face_crop",
  "stream_id": "lounge-session-001",
  "track_id": "track-a81b2c3d4e5f",
  "crop_id": "crop-0123456789abcdef01234567",
  "image_b64": "<base64-encoded JPEG crop>",
  "mime_type": "image/jpeg",
  "emitted_at": "2026-10-15T09:00:00+00:00"
}
```

Cache the image by `crop_id` on the phone and associate it with the matching `track_id`. Do not expect the full image to be repeated in every snapshot. If a crop delivery fails or lounge-control no longer has the referenced crop, the worker retries that crop with its next refresh. The `guest_id` is a stable opaque guest-profile ID; `track_id` identifies one temporary face track and may change if the worker loses and reacquires the face or the stream restarts. `preferences` and `allergies` are separate lists; the optional `alert` is the concise display string for the allergy cue.

Lounge-control keeps each stable match for five seconds after the worker's `matched_at` observation time, not callback arrival time; callbacks older than five seconds are ignored. A worker refreshes active tracks only when a current detection supports the same candidate identity. Crops are cached only from identity-matched detections, and a track with strong evidence for another guest is not reused for the new identity. An explicit no-match, guest departure, or WebSocket disconnect clears the corresponding result sooner. A crop can arrive just before its person entry, with a periodic snapshot in between, so phone clients should keep an unreferenced crop pending for up to five seconds instead of discarding it on the first snapshot that omits it. Refresh its local expiry whenever a snapshot references it; expire it five seconds after its last reference, or after five seconds without a newer snapshot if the connection drops. The face worker's separate 2.5-second tracking timeout is unchanged. Frames and crops remain transient in memory and are never written to disk.

The snapshot schema is [`contracts/detection-set.schema.json`](contracts/detection-set.schema.json), the crop message schema is [`contracts/face-crop.schema.json`](contracts/face-crop.schema.json), the raw debug message schema is [`contracts/debug-frame.schema.json`](contracts/debug-frame.schema.json), and the internal worker callback schema is [`contracts/match-event.schema.json`](contracts/match-event.schema.json).

The laptop dashboard's **Face Recognition Test** now shows the received cropped images and their matching guest metadata together. Use **Start video stream (1 fps)** to grant browser camera access, open one authenticated WebSocket to port `8003`, and send JPEG frames continuously until **Stop video stream** is pressed; stopping also turns the camera off. Open the dashboard on `localhost` or HTTPS for browser camera access. This laptop-camera test exercises the same video-stream endpoint as a phone client, but does not connect to the Rokid glasses; the Android glasses app is not implemented yet. Try the generated [two-person scene](fixtures/synthetic_multi_face.png) with its [left-person reference crop](fixtures/synthetic_guest_left.jpg) and [right-person reference crop](fixtures/synthetic_guest_right.jpg); the full setup is in the [synthetic multi-person demo guide](docs/architecture/face-recognition-demo.md#synthetic-two-person-test).

---

### Simulators & Replay Workflows

The `sim` profile includes `tap-simulator` and `frame-replay`.

#### Running Core Services with Tap Simulator

Start the stack with continuous simulated card-reader taps:

```bash
docker compose --profile sim up --build --wait lounge-control face-worker mock-hotel tap-simulator
```

#### One-Shot Frame Replay

Admit Alex in the dashboard first, then run the one-shot replay. It sends three frames of the fictional synthetic face through the real device WebSocket interface and waits for the recognition cue. The image is a local test fixture, not a real guest photo:

```bash
docker compose --profile sim run --rm frame-replay
```

To specify custom options or a custom fixture:

```bash
docker compose --profile sim run --rm frame-replay --fixture /path/to/consented_frame.jpg --frames 5
```

The replay client connects, transmits three frames by default, logs transmission metrics (without logging frame payloads), listens for cues, and cleanly exits. This confirms that the same synthetic reference and replay image produce a stable match in the local POC; it is not an accuracy or real-world performance evaluation.

---

### Running Automated Checks

To run the automated tests outside of AGY:

```bash
python3 -m pip install -r requirements-test.txt
python3 -m pytest
```
