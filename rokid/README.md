# Rokid Glass3 face recognition

The glasses track faces locally; the Python server recognizes faces and returns names for labels beside the tracked people.

This folder contains a standalone demo with a Kotlin Android app running on the glasses and a Python FastAPI server running on a laptop. CameraX supplies frames to a bundled ML Kit face detector on the glasses. Periodically, a selected face crop is encoded as JPEG and sent over HTTP on a reachable Wi-Fi network for InsightFace **buffalo_l** identity recognition on the laptop's CPU, matching the model pack in the main project's README. No Google Play Services model download is required.

## Components

| Location | Purpose |
| --- | --- |
| `app/` | Android app for camera capture, server communication, and text display on the glasses. |
| `app/src/main/java/com/example/rokid_app/MainActivity.kt` | Manages camera permission, automatic capture, connection retries, and displayed results. |
| `app/src/main/java/com/example/rokid_app/FaceServerClient.kt` | Checks server health and uploads JPEGs for recognition. |
| `server/app.py` | FastAPI server with `GET /health` and `POST /detect`. |
| `server/recognition.py` | InsightFace buffalo_l: SCRFD detection/alignment and ArcFace identity matching through ONNX Runtime CPU. |
| `server/faces/` | Reference-photo gallery; each image filename supplies the person's name. |
| `server/setup.py` | Creates the Python environment, installs dependencies, and downloads recognition models. |
| `server/run.py` | Starts the server, normally on port 8000, with a configurable matching threshold. |
| `gradle.properties` | Configures the laptop server address compiled into the Android app. |

## Pipeline

1. **Load the gallery:** At server startup, images in server/faces/ are converted into normalized 512-value ArcFace feature vectors and cached in memory. Each filename becomes the person's name. Reference images with zero or multiple detected faces are skipped.
2. **Track and send:** A single temple tap starts detection and a 15-second silence timer. Locally detected speech resets the timer; after 15 seconds without detected speech, camera capture and microphone monitoring stop and the display returns to black. During that window, the glasses analyze the latest camera frame at most every 80 ms, targeting 960 × 720 (the actual resolution may differ). Frames arriving while detection is busy are dropped. Only a guest whose face center lies within the central 30% of both axes of the calibrated display is eligible; if several qualify, the closest to the center is selected. About every two seconds, the selected face and padding (1.6 times its detected width/height, clipped at image edges) are encoded as a JPEG crop for recognition. No recognition request is sent while idle or without a centered guest. Only one server request runs at a time.
3. **Recognize:** The server rotates the image upright and uses InsightFace buffalo_l with SCRFD detection/landmarks and ArcFace embeddings. Each vector is compared against the gallery using cosine similarity. A match must pass both the score threshold and the required lead over the second-best identity; otherwise it returns Unknown.
4. **Display:** Server face boxes are mapped from the JPEG crop back into the original upright frame and matched against the selected local track. Unambiguous matches label the current track beside its face, with text size bounded by readable limits. Matches below the recognition threshold show **Unknown**. Leaving the center clears the box/name and invalidates pending identities. Lost tracks, ambiguous associations, responses older than two seconds, and identities older than four seconds are discarded. Labels disappear within 500 ms if tracking stalls. Debug boxes have 12% visual padding, independent of optical calibration. There is no visible camera preview. This uses head direction as a proxy for attention; it does not measure eye contact. The padded crop can include parts of other people if they overlap the selected guest.

Gallery vectors are rebuilt on every server restart. Incoming camera images are processed in memory and are not saved.

## Temple touch and audio silence timeout

The camera and microphone stay closed while idle; server health checks continue.
A temple tap starts a new session with a 15-second deadline. AudioRecord uses the
standard MIC source: on this RV101, VOICE_RECOGNITION initializes without error
but supplies only zero-valued samples. The firmware also reports silenced=true
for MIC even when real samples arrive, so tests validate the signal rather than
trusting that flag alone. This agrees with a separate [first-hand RV101 microphone
investigation](https://zenn.dev/maruhana/articles/rokid-conversation-support-03?locale=en).
WebRTC VAD 2.0.10
runs locally on 16 kHz mono, signed 16-bit PCM in 20 ms frames, using its
VERY_AGGRESSIVE mode and a short speech-duration filter. It detects speech-like
activity rather than resetting on every loud sound. During an activation, audio
associated with a stable recognized guest is buffered in memory. On the natural
silence timeout it is uploaded for local Whisper transcription and Gemini
preference extraction, as described below. Idle audio is never captured.

Each speech observation resets the deadline to 15 seconds after that observation
without changing the scan ID, so valid pending identities remain associated with
the same session. Speech cannot activate idle detection or revive an expired
session. Another temple tap starts a new session. A status swipe neither starts
nor extends recognition. Expiry closes the camera and microphone, clears labels,
and cancels pending face uploads while leaving health checks enabled. A completed
preference upload runs separately after capture stops. Backgrounding
the app also stops capture. Microphone permission denial or initialization/read
failure leaves/stops detection with a retry message instead of pretending the
audio timeout is working.

An in-flight HTTP request follows the extended scan deadline while retaining
independent 3-second connect, 10-second read, and 12-second overall limits.
Stopping/expiring a scan still cancels it. Speech/VAD is not speaker recognition:
nearby conversations, television speech and false positives can keep a session
active, while quiet/occluded speech can be missed. Validate it in the intended
restaurant noise; these settings do not establish speech-detection accuracy.

Implementation references: [Android AudioRecord](https://developer.android.com/reference/android/media/AudioRecord)
and [the pinned Android WebRTC VAD implementation](https://github.com/gkonovalov/android-vad/tree/2.0.10).
The JitPack repository is restricted to that dependency group.

To inspect timing without recording audio:

~~~text
adb logcat -v threadtime -s FaceAudio:I FaceInteraction:I FaceConnection:I "*:S"
~~~

`FaceAudio` reports microphone start/stop and throttled speech-activity events,
not PCM or recognized words. Unit tests cover the 15-second boundary, continuous
speech, stale callbacks, retaps and status swipes. Device tests cover native VAD
on silence/synthetic speech, actual microphone stop/reopen, and HTTP requests
surviving deadline extension as well as expiry and cancellation.

Validation on **2026-11-02**: all 30 JVM tests and eight device tests (including the opt-in production-input probe) passed;
debug build and lint passed with no errors. On the cleaned MIC-source build, a speech event at 14.782 seconds extended a
fresh capture session to 30.195 seconds. Capture stopped 15.413 seconds after
that last logged speech event, the microphone was released, and server health
checks continued online over the debug USB transport. A separate quiet-room
capture had zero speech detections and stopped after approximately 15.4 seconds.
This does not establish speech/noise accuracy in a restaurant. The test APK's
speech fixture is offline-generated speech, not a recording of a person.
An opt-in `AudioInputProbeTest` opens the exact production recorder in a foreground
Activity and checks actual nonzero samples; it caught the VOICE_RECOGNITION input
regression that start/stop-only tests missed. Run it with `-e audio_probe true`;
`-e expect_speech true -e frames 1000` additionally checks 20 seconds of live speech
when a wearer is available. Only aggregate levels and VAD counts are logged.

## Conversation preferences

A temple tap starts the existing face/speech session. Keep one enrolled guest
centered and wait for their name to settle (two matching recognition responses)
before saying a preference. After 15 seconds without detected speech, the glasses
stop capture and send the buffered WAV to `POST /audio/preferences`. Local
faster-whisper **base**, CPU int8, transcribes it; **Gemini 3.8 Flash** extracts
structured preferences; SQLite saves them against the recognized gallery name.
This model replaces 2.5 Flash following the project's live API availability check.

Copy `server/.env.example` to `server/.env`, set `GEMINI_API_KEY`, then run
`server/setup.py` to install/cache models and restart `server/run.py`.
The ignored environment file also configures `GEMINI_MODEL`, `WHISPER_MODEL` and
`WHISPER_LANGUAGE` (default `en`; empty enables language detection).
`PREFERENCES_DB` optionally overrides `server/data/preferences.sqlite3`.
`GET /health` reports configuration, not a successful Google availability probe.
Inspect saved profiles at `http://localhost:8000/guests`, or fetch one profile
at `/guests/{guest_id}/preferences`.

Supported fields are coffee, tea, water, diet, food, room view/floor/type, seating
and service. A later statement updates the same guest/field. Each value includes
an exact supporting quote and timestamp. Capture IDs prevent duplicate writes.
Failed transcription/extraction leaves the database unchanged. Google transient
errors receive one bounded retry; failures are logged without conversation text.

The glasses accept audio only while the same stable identity is visible and
recently confirmed. A different recognized person discards the whole recording.
Retapping, backgrounding, or input failures also discard unfinished recordings.
Audio is limited to 90 seconds per activation; overflow discards the recording.
There is no durable upload queue, so a failed upload must be captured again.
Preference processing uses a separate worker from recognition and health checks.

This POC assumes one guest per conversation. Face recognition and VAD do not
identify individual speakers. The extraction prompt rejects ambiguous attribution,
staff personal preferences, unanswered questions, instructions embedded in the
transcript, and medical/allergy information; this is not a guarantee of perfect
speaker attribution or factual accuracy. Gallery names must uniquely identify
demo guests. Review extracted facts before using them operationally.

Staged checks (synthetic speech, separate test databases):

```powershell
server/.venv/Scripts/python.exe -m unittest server.test_audio_preferences server.test_preference_api server.test_app server.test_recognition
server/.venv/Scripts/python.exe server/check_audio_pipeline.py --stage whisper --audio .artifacts/audio-preferences/preference-test.wav
server/.venv/Scripts/python.exe server/check_audio_pipeline.py --stage gemini
server/.venv/Scripts/python.exe server/check_audio_pipeline.py --stage full --audio .artifacts/audio-preferences/preference-test.wav
```

The WAV is a locally generated test fixture, not supplied by setup. The model
checks need the configured key and internet access. Unit/API tests substitute
models; they establish contracts and persistence, not live Gemini availability.
The opt-in Android `PreferencePipelineDeviceTest` exercises real recognition,
native VAD, WAV buffering/upload, cloud extraction and database idempotency.
Run it only against an isolated staging database, with `-e preference_e2e true`
and `-e server http://127.0.0.1:8004` after setting up USB port forwarding and
the device-private `files/preference-fixture.jpg` enrollment fixture.

Validation on **2026-11-02**:

| Stage | Result |
| --- | --- |
| SQLite, WAV validation, guest binding, extraction filtering and HTTP regressions | 34 server tests passed; models substituted in contract tests |
| Capture policy and existing interaction/recognition logic | 37 JVM tests passed |
| Android build and lint | Passed; no lint errors |
| Native VAD, microphone frames, transport and existing device regressions | 10 device tests passed; opt-in cloud test separately executed |
| Actual local Whisper base | Transcribed the 7.16-second synthetic preference clip in 1.16 seconds after model load |
| Actual Gemini 3.8 Flash | Blocked by provider HTTP 503/504; minimal Interactions request also timed out |
| Full device replay | Real face matching and audio upload reached the server, then failed at Gemini with HTTP 503; staging database remained empty and health stayed responsive |

Cloud extraction and the complete live-model save path have **not passed**.
Repeat the live-model checks when the provider recovers before calling this
feature end-to-end validated. Controlled replay does not establish real-room
transcription, recognition, or preference-extraction accuracy.

## Data handling

- Reference photos remain on disk in `server/faces/`; model files are downloaded into `server/models/` by setup.
- Derived gallery feature vectors are cached in server memory and rebuilt at startup. Restart the server after changing gallery photos.
- Incoming camera JPEGs are processed in memory without being saved to disk.
- Activated, identity-bound audio is transient in memory on glasses/server. Whisper runs locally; the transcript and guest name are sent to Google's Gemini service for extraction. Full audio/transcripts are not written to disk by this feature. SQLite persists extracted values and supporting transcript excerpts; its directory and `.env` are ignored by Git. This demo API is intended for a trusted test network.
- The server returns detected face names, similarity scores, bounding boxes, and display text. Multiple detected faces can be included in one response.
- Server logs include recognition names and scores. Android Logcat includes capture, request, and processing timings.
- Matching uses a similarity threshold per image; it does not apply the main hotel worker's multi-observation stability checks. The reported latency measurements below do not establish recognition accuracy.

## Setup and start

### 1. Set up the server once

Install Python **3.12**. Run the following server commands from the `rokid/` directory:

~~~text
python server/setup.py
~~~

This creates server/.venv, installs InsightFace 2.1.0 and ONNX Runtime 1.30.0, and downloads the buffalo_l model pack into server/models/insightface/. Internet access is required for initial setup. The Python scripts work on Windows, macOS, and Linux. InsightFace is installed with --no-deps, as in the main project's face-worker, to reuse the headless OpenCV dependency. Only the detection and recognition modules are enabled, with a fixed 640 x 640 detector input and CPU inference.

### 2. Add face images

Put clear photos in server/faces/, for example:

~~~text
server/faces/
  Ping Hui.jpg
  Alex.png
~~~

The supplied Ping Hui.jpg is already included. Use exactly one person per photo; ambiguous enrollment photos are skipped. Restart the server after changing gallery images. The health response reports model, execution providers, gallery_names, and gallery_templates so enrollment can be verified.

### 3. Start the server

~~~text
python server/run.py
~~~

Keep the terminal open. The server uses CPU inference and listens on port **8000**. To change the matching threshold:

~~~text
python server/run.py --threshold 0.50 --margin 0.10
~~~

The provisional defaults are **0.50** cosine similarity and a **0.10** lead over the second-best identity. The score threshold was lowered from the main project's initial 0.65 after frequent Unknown results during glasses testing. This makes matching more permissive and may increase wrong-name matches; both settings still need representative validation. These use a different embedding model from the old SFace threshold of 0.363. Cosine similarity is not a percentage confidence. This standalone endpoint applies score and margin checks per image; it does not implement the main worker's two-of-three temporal voting or active-cohort service.

### Why ML Kit remains on the glasses

ML Kit supplies fast local face positions and temporary tracking IDs during each tap-activated session. It selects a centered guest and keeps their name near their face between server uploads. It does not identify the person. InsightFace runs on the laptop and supplies identity matching. Removing ML Kit would require another local tracker or more frequent full-frame server processing, with label updates dependent on network and server latency. Both local detection and server recognition are idle outside the tap-activated window; lightweight health checks continue.

The buffalo_l pretrained weights are provided by InsightFace for non-commercial research; commercial deployment needs an appropriately licensed model. See the [main project's model notes](../apps/face-worker/MODELS.md) and [InsightFace's model documentation](https://github.com/deepinsight/insightface/tree/master/python-package).

On **2026-10-30**, a local HTTP round-trip check enrolled all five gallery identities and returned the expected name for each reference photo, repeated twice. CPU inference averaged **216 ms**, with a **203–250 ms** range across ten requests, using four ONNX Runtime threads and a fixed 640 x 640 detector input. These reused enrollment images, so the check verifies model loading and API wiring rather than recognition accuracy. The timing excludes the glasses camera and Wi-Fi path.

### 4. Run the glasses app

Connect the laptop and glasses to the same reachable Wi-Fi network. Set the laptop's address in gradle.properties:

~~~properties
faceServerUrl=http://YOUR_LAPTOP_IP:8000
~~~

In Android Studio, select the glasses and click **Run** to build, install, and launch the app. On the first temple tap, grant camera and microphone permissions. The app stays black while checking the server in the background. Tap once to activate detection; speech resets a 15-second silence timer, and 15 seconds without detected speech returns the app to idle. Swipe forward to show the connection icon for five seconds. Rebuild/reinstall if the server address changes.

## Previous SFace recognition latency check

Measured using the previous SFace backend on the connected glasses over Wi-Fi on **2026-10-27**, after replacing full-frame per-pixel YUV copying with bulk copying of the selected crop. Across 14 uploads, analysis callback to parsed server response averaged **200 ms**, with a **79–321 ms** range. Thirteen responses contained a detected face; this small diagnostic sample does not establish recognition accuracy or buffalo_l performance. The timing excludes sensor delivery, waiting for a centered face/the next upload, and display presentation. Before this fix, recognition frames spent approximately **2.2–2.4 seconds** in local preparation, exceeding the two-second response freshness limit and causing otherwise successful results to be discarded.

Two Android device tests use a deliberately stalled local HTTP endpoint to verify that deadline expiry and explicit scan cancellation interrupt recognition while preserving subsequent health checks. Server work already received before cancellation may still complete; continuing `GET /health` after scan expiry is expected.

## Previous still-capture latency (before local tracking)

Measured on the Rokid glasses over Wi-Fi on **2026-10-22**, across **30 captures** after the initial capture. Eleven samples contained a detected face.

| Stage | Average |
| --- | ---: |
| Camera capture and JPEG delivery | 637 ms |
| Upload, server processing, and response | 307 ms |
| **Capture request to received response** | **944 ms** |

Server face processing averaged **69 ms**, included in the 307 ms above. Total latency had a **943 ms median**, a **777-1,122 ms range**, and a **1,114 ms 95th percentile**. The first capture took **1,255 ms**.

Camera capture/JPEG delivery was the largest component. These measurements end when the response is parsed on the glasses; they exclude waiting for the next two-second capture and physical display presentation.

These historical measurements do not describe the new analysis pipeline. Current **FaceLatency** logs report analysis callback to server response (including local detection, JPEG encoding, and networking), server inference time, and face count. They exclude camera sensor delivery and physical display presentation. To view them, filter Android Studio Logcat by **FaceLatency**, or run:

~~~text
adb logcat -v threadtime -s FaceLatency:I "*:S"
~~~
