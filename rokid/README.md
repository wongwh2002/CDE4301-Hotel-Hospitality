# Rokid Glass3 face recognition

The glasses capture images; the Python server recognizes faces and returns names for the glasses to display.

## Pipeline

1. **Load the gallery:** At server startup, images in server/faces/ are converted into SFace feature vectors and cached in memory. Each filename becomes the person's name.
2. **Capture and send:** The glasses send one full, uncropped JPEG about every two seconds. Only one request runs at a time.
3. **Recognize:** The server rotates the image upright, detects faces with OpenCV YuNet, then aligns each face and extracts its SFace vector. Each vector is compared against all gallery vectors using cosine similarity.
4. **Display:** The best match above the threshold becomes the name. Otherwise, the glasses display **Unknown**, or **No face detected** when no face is found. The display shows text only.

Gallery vectors are rebuilt on every server restart. Incoming camera images are processed in memory and are not saved.

## Setup and start

### 1. Set up the server once

Install Python **3.12**. From the project root, run:

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
