# Rokid Glass3 face recognition

The glasses capture images; the Python server recognizes faces and returns names for the glasses to display.

This folder contains a standalone demo with a Kotlin Android app running on the glasses and a Python FastAPI server running on a laptop. The app accesses the glasses camera directly through Android CameraX and sends images over HTTP on a reachable Wi-Fi network. Face detection and identity matching run on the laptop's CPU.

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

## Relationship to the hotel POC

This demo currently operates separately from the [main hotel smart-glasses POC](../README.md). It uses its own server, reference-photo gallery, and YuNet/SFace models. It does not yet connect to `lounge-control`, `face-worker`, or `mock-hotel`.

The demo compares detected faces against the entire local gallery. Lounge entry/exit events, the active lounge cohort, hotel guest profiles, and allergy or preference cues are not integrated. The glasses show recognition names and status text. Connecting this app to the hotel backend requires adapting its HTTP request/response flow to the backend's authenticated WebSocket frame and cue protocol.

Both servers default to host port 8000. When running this server alongside the main Compose stack, choose another port with `python server/run.py --port 8010` and update `faceServerUrl` accordingly before rebuilding the app.

## Pipeline

1. **Load the gallery:** At server startup, images in server/faces/ are converted into SFace feature vectors and cached in memory. Each filename becomes the person's name.
2. **Capture and send:** The glasses send one full, uncropped JPEG about every two seconds. Only one request runs at a time.
3. **Recognize:** The server rotates the image upright, detects faces with OpenCV YuNet, then aligns each face and extracts its SFace vector. Each vector is compared against all gallery vectors using cosine similarity.
4. **Display:** The best match above the threshold becomes the name. Otherwise, the glasses display **Unknown**, or **No face detected** when no face is found. The display shows text only.

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

## Measured latency

Measured on the Rokid glasses over Wi-Fi on **2026-10-22**, across **30 captures** after the initial capture. Eleven samples contained a detected face.

| Stage | Average |
| --- | ---: |
| Camera capture and JPEG delivery | 637 ms |
| Upload, server processing, and response | 307 ms |
| **Capture request to received response** | **944 ms** |

Server face processing averaged **69 ms**, included in the 307 ms above. Total latency had a **943 ms median**, a **777-1,122 ms range**, and a **1,114 ms 95th percentile**. The first capture took **1,255 ms**.

Camera capture/JPEG delivery was the largest component. These measurements end when the response is parsed on the glasses; they exclude waiting for the next two-second capture and physical display presentation.

To view ongoing timing measurements in Android Studio Logcat, filter by **FaceLatency**, or run:

~~~text
adb logcat -v threadtime -s FaceLatency:I "*:S"
~~~
