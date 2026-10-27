# Rokid Glass3 face recognition

The glasses track faces locally; the Python server recognizes faces and returns names for labels beside the tracked people.

This folder contains a standalone demo with a Kotlin Android app running on the glasses and a Python FastAPI server running on a laptop. CameraX supplies frames to a bundled ML Kit face detector on the glasses. Periodically, the same frame is encoded as JPEG and sent over HTTP on a reachable Wi-Fi network for YuNet/SFace identity recognition on the laptop's CPU. No Google Play Services model download is required.

## Components

| Location | Purpose |
| --- | --- |
| `app/` | Android app for camera capture, server communication, and text display on the glasses. |
| `app/src/main/java/com/example/rokid_app/MainActivity.kt` | Manages camera permission, automatic capture, connection retries, and displayed results. |
| `app/src/main/java/com/example/rokid_app/FaceServerClient.kt` | Checks server health and uploads JPEGs for recognition. |
| `server/app.py` | FastAPI server with `GET /health` and `POST /detect`, YuNet face detection, and SFace identity matching. |
| `server/faces/` | Reference-photo gallery; each image filename supplies the person's name. |
| `server/setup.py` | Creates the Python environment, installs dependencies, and downloads recognition models. |
| `server/run.py` | Starts the server, normally on port 8000, with a configurable matching threshold. |
| `gradle.properties` | Configures the laptop server address compiled into the Android app. |

## Pipeline

1. **Load the gallery:** At server startup, images in server/faces/ are converted into SFace feature vectors and cached in memory. Each filename becomes the person's name.
2. **Track and send:** A single temple tap starts a ten-second detection window. During that window, the glasses analyze the latest camera frame at most every 80 ms, targeting 960 × 720 (the actual resolution may differ). Frames arriving while detection is busy are dropped. Only a guest whose face center lies within the central 30% of both axes of the calibrated display is eligible; if several qualify, the closest to the center is selected. About every two seconds, the selected face and padding (1.6 times its detected width/height, clipped at image edges) are encoded as a JPEG crop for recognition. No recognition request is sent while idle or without a centered guest. Only one server request runs at a time.
3. **Recognize:** The server rotates the image upright, detects faces with OpenCV YuNet, then aligns each face and extracts its SFace vector. Each vector is compared against all gallery vectors using cosine similarity.
4. **Display:** Server face boxes are mapped from the JPEG crop back into the original upright frame and matched against the selected local track. Unambiguous matches label the current track beside its face, with text size bounded by readable limits. Matches below the recognition threshold show **Unknown**. Leaving the center clears the box/name and invalidates pending identities. Lost tracks, ambiguous associations, responses older than two seconds, and identities older than four seconds are discarded. Labels disappear within 500 ms if tracking stalls. Debug boxes have 12% visual padding, independent of optical calibration. There is no visible camera preview. This uses head direction as a proxy for attention; it does not measure eye contact. The padded crop can include parts of other people if they overlap the selected guest.

Gallery vectors are rebuilt on every server restart. Incoming camera images are processed in memory and are not saved.

## Data handling

- Reference photos remain on disk in `server/faces/`; model files are downloaded into `server/models/` by setup.
- Derived gallery feature vectors are cached in server memory and rebuilt at startup. Restart the server after changing gallery photos.
- Incoming camera JPEGs are processed in memory without being saved to disk.
- The server returns detected face names, similarity scores, bounding boxes, and display text. Multiple detected faces can be included in one response.
- Server logs include recognition names and scores. Android Logcat includes capture, request, and processing timings.
- Matching uses a similarity threshold per image; it does not apply the main hotel worker's multi-observation stability checks. The reported latency measurements below do not establish recognition accuracy.

## Setup and start

### 1. Set up the server once

Install Python **3.12**. Run the following server commands from the `rokid/` directory:

~~~text
python server/setup.py
~~~

This creates server/.venv, installs dependencies, and downloads the YuNet/SFace models. Internet access is required for setup. The Python scripts work on Windows, macOS, and Linux.

### 2. Add face images

Put clear photos in server/faces/, for example:

~~~text
server/faces/
  Ping Hui.jpg
  Alex.png
~~~

The supplied Ping Hui.jpg is already included. Use one person per photo; the server selects the largest detected face. Restart the server after changing gallery images.

### 3. Start the server

~~~text
python server/run.py
~~~

Keep the terminal open. The server uses CPU inference and listens on port **8000**. To change the matching threshold:

~~~text
python server/run.py --threshold 0.363
~~~

The default threshold is **0.363**; cosine similarity is not a percentage confidence.

### 4. Run the glasses app

Connect the laptop and glasses to the same reachable Wi-Fi network. Set the laptop's address in gradle.properties:

~~~properties
faceServerUrl=http://YOUR_LAPTOP_IP:8000
~~~

In Android Studio, select the glasses and click **Run** to build, install, and launch the app. Grant camera permission. Once **Connected to server** appears, capture and recognition run automatically. Rebuild/reinstall if the server address changes.

## Current recognition latency check

Measured on the connected glasses over Wi-Fi on **2026-10-27**, after replacing full-frame per-pixel YUV copying with bulk copying of the selected crop. Across 14 uploads, analysis callback to parsed server response averaged **200 ms**, with a **79–321 ms** range. Thirteen responses contained a detected face; this small diagnostic sample does not establish recognition accuracy. The timing excludes sensor delivery, waiting for a centered face/the next upload, and display presentation. Before this fix, recognition frames spent approximately **2.2–2.4 seconds** in local preparation, exceeding the two-second response freshness limit and causing otherwise successful results to be discarded.

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
