"""Laptop Dashboard UI for Hotel Lounge Smart-Glasses POC.

Served directly from lounge-control. Allows staff to:
- Select a guest from hotel records or manually edit guest_ref
- Submit entry and exit taps via the shared /v1/lounge/taps path
- View live active roster displaying display_name and admitted_at only
- Automatically refetch roster on SSE roster_change events
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hotel Lounge Staff Dashboard</title>
  <style>
    :root {
      --bg-color: #0f172a;
      --card-bg: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-hover: #0284c7;
      --success: #22c55e;
      --success-hover: #16a34a;
      --danger: #ef4444;
      --danger-hover: #dc2626;
      --border: #334155;
    }
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    body {
      background-color: var(--bg-color);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    h1 {
      font-size: 1.25rem;
      font-weight: 600;
      letter-spacing: -0.025em;
    }
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.85rem;
      color: var(--text-muted);
      background: rgba(255, 255, 255, 0.05);
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      border: 1px solid var(--border);
    }
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #eab308;
    }
    .status-dot.connected {
      background: var(--success);
      box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
    }
    main {
      flex: 1;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
      padding: 2rem;
      max-width: 1400px;
      margin: 0 auto;
      width: 100%;
    }
    @media (max-width: 860px) {
      main {
        grid-template-columns: 1fr;
      }
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 0.75rem;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }
    h2 {
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--accent);
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }
    label {
      font-size: 0.85rem;
      color: var(--text-muted);
      font-weight: 500;
    }
    select, input[type="text"], input[type="password"], input[type="file"] {
      background: #0f172a;
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 0.6rem 0.75rem;
      border-radius: 0.375rem;
      font-size: 0.95rem;
      outline: none;
      transition: border-color 0.15s;
    }
    select:focus, input[type="text"]:focus, input[type="password"]:focus, input[type="file"]:focus {
      border-color: var(--accent);
    }
    .btn-row {
      display: flex;
      gap: 1rem;
      margin-top: 0.5rem;
    }
    button {
      flex: 1;
      padding: 0.75rem 1rem;
      border-radius: 0.375rem;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      border: none;
      transition: background-color 0.15s, opacity 0.15s;
    }
    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    .btn-entry {
      background: var(--success);
      color: white;
    }
    .btn-entry:hover:not(:disabled) {
      background: var(--success-hover);
    }
    .btn-exit {
      background: var(--danger);
      color: white;
    }
    .btn-exit:hover:not(:disabled) {
      background: var(--danger-hover);
    }
    .btn-register {
      background: var(--accent);
      color: #082f49;
    }
    .btn-register:hover:not(:disabled) {
      background: var(--accent-hover);
      color: white;
    }
    .btn-refresh {
      background: transparent;
      border: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 0.8rem;
      padding: 0.25rem 0.5rem;
      border-radius: 0.25rem;
      cursor: pointer;
    }
    .btn-refresh:hover {
      color: var(--text-main);
      border-color: var(--text-muted);
    }
    .btn-camera {
      background: var(--accent);
      color: #082f49;
    }
    .btn-secondary {
      background: #475569;
      color: var(--text-main);
    }
    .cv-actions {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.75rem;
    }
    .photo-actions {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.75rem;
    }
    .photo-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.75rem;
    }
    .photo-card {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      min-width: 0;
      color: var(--text-muted);
      font-size: 0.8rem;
    }
    .photo-card img {
      width: 100%;
      aspect-ratio: 1;
      object-fit: cover;
      background: #020617;
      border: 1px solid var(--border);
      border-radius: 0.375rem;
    }
    .photo-remove {
      flex: 0 0 auto;
      padding: 0.4rem;
      background: #475569;
      color: var(--text-main);
      font-size: 0.8rem;
    }
    .media-preview {
      display: block;
      width: 100%;
      max-height: 320px;
      object-fit: contain;
      background: #020617;
      border: 1px solid var(--border);
      border-radius: 0.375rem;
    }
    .media-preview[hidden] {
      display: none;
    }
    .help-text {
      color: var(--text-muted);
      font-size: 0.8rem;
      line-height: 1.45;
    }
    .feedback {
      padding: 0.75rem 1rem;
      border-radius: 0.375rem;
      font-size: 0.875rem;
      display: none;
    }
    .feedback.info {
      display: block;
      background: rgba(56, 189, 248, 0.15);
      border: 1px solid var(--accent);
      color: var(--accent);
    }
    .feedback.error {
      display: block;
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid var(--danger);
      color: #fca5a5;
    }
    .feedback.success {
      display: block;
      background: rgba(34, 197, 94, 0.15);
      border: 1px solid var(--success);
      color: #86efac;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }
    th {
      text-align: left;
      padding: 0.6rem 0.75rem;
      border-bottom: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    td {
      padding: 0.75rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    tr:last-child td {
      border-bottom: none;
    }
    .empty-state {
      text-align: center;
      padding: 2.5rem 1rem;
      color: var(--text-muted);
      font-style: italic;
      font-size: 0.9rem;
    }
    .counter {
      background: rgba(56, 189, 248, 0.2);
      color: var(--accent);
      padding: 0.1rem 0.45rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      margin-left: 0.5rem;
    }
    .privacy-notice {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: auto;
      padding-top: 1rem;
      border-top: 1px dashed var(--border);
    }
  </style>
</head>
<body>
  <header>
    <h1>🏨 Hotel Lounge — Laptop Control & Roster</h1>
    <div class="status-badge" id="sse-status">
      <span class="status-dot" id="sse-dot"></span>
      <span id="sse-text">Connecting SSE...</span>
    </div>
  </header>

  <main>
    <!-- Tap Control Card -->
    <div class="card">
      <h2>Guest Tap Ingress</h2>

      <div class="form-group">
        <label for="guest-dropdown">Select Registered Hotel Guest</label>
        <select id="guest-dropdown">
          <option value="">-- Choose guest or type reference below --</option>
        </select>
      </div>

      <div class="form-group">
        <label for="guest-ref">Guest Reference (editable)</label>
        <input type="text" id="guest-ref" placeholder="e.g. guest-alex-101" spellcheck="false" autocomplete="off" />
      </div>

      <div class="btn-row">
        <button type="button" class="btn-entry" id="btn-entry" onclick="submitTap('entry')">
          🟢 Admit (Entry Tap)
        </button>
        <button type="button" class="btn-exit" id="btn-exit" onclick="submitTap('exit')">
          🔴 Depart (Exit Tap)
        </button>
      </div>

      <div id="tap-feedback" class="feedback"></div>

      <div class="privacy-notice">
        Submits taps to <code>POST /v1/lounge/taps</code>. Enforces at most one active presence per guest reference.
      </div>
    </div>

    <!-- Mock Hotel Guest Registration Card -->
    <div class="card">
      <h2>Register Mock Hotel Guest</h2>
      <form id="guest-registration-form">
        <div class="form-group">
          <label for="guest-name">Guest name</label>
          <input type="text" id="guest-name" maxlength="100" required autocomplete="off" />
        </div>
        <div class="form-group">
          <label for="guest-room">Room number (optional)</label>
          <input type="text" id="guest-room" autocomplete="off" />
        </div>
        <div class="form-group">
          <label for="guest-allergies">Allergies (optional, comma-separated)</label>
          <input type="text" id="guest-allergies" placeholder="e.g. peanuts, shellfish" />
        </div>
        <div class="form-group">
          <label for="guest-preferences">Preferences (optional, comma-separated)</label>
          <input type="text" id="guest-preferences" placeholder="e.g. still water, quiet table" />
        </div>
        <div class="form-group">
          <label for="guest-photo-files">Face reference photos (up to 3)</label>
          <input type="file" id="guest-photo-files" accept="image/*" capture="user" multiple />
          <div class="help-text">Add clear photos of one face. A front-facing photo plus slight left/right angles is a useful start. Photos are resized to JPEG before saving. Live camera preview needs localhost or HTTPS; on a phone over plain LAN HTTP, use the photo picker’s camera option if available.</div>
        </div>
        <div class="photo-actions">
          <button type="button" class="btn-camera" id="guest-camera-start">Open camera</button>
          <button type="button" class="btn-register" id="guest-camera-capture" disabled>Capture photo</button>
          <button type="button" class="btn-secondary" id="guest-camera-stop" disabled>Stop camera</button>
        </div>
        <video id="guest-camera-preview" class="media-preview" autoplay playsinline muted hidden></video>
        <div class="help-text" id="guest-photo-count">0 of 3 photos selected</div>
        <div id="guest-photo-previews" class="photo-grid" aria-live="polite"></div>
        <button type="submit" class="btn-register" id="btn-register-guest">Register guest</button>
      </form>
      <div id="registration-feedback" class="feedback" role="status" aria-live="polite"></div>
      <div class="privacy-notice">
        Saves up to three JPEG reference photos in the local mock-hotel database for re-enrollment. This POC has no per-guest photo deletion yet; photos remain in its Docker data volume until that volume is removed. The face-worker keeps derived templates in memory while a guest is admitted. Use synthetic or consented demo photos.
      </div>
    </div>

    <!-- Active Roster Card -->
    <div class="card">
      <h2>
        <span>Active Lounge Roster <span class="counter" id="roster-count">0</span></span>
        <button type="button" class="btn-refresh" onclick="fetchRoster()">Refresh</button>
      </h2>

      <div id="roster-container">
        <table>
          <thead>
            <tr>
              <th>Guest Name</th>
              <th>Admitted At</th>
            </tr>
          </thead>
          <tbody id="roster-tbody">
            <!-- Dynamic entries -->
          </tbody>
        </table>
        <div id="roster-empty" class="empty-state">No guests currently admitted in lounge.</div>
      </div>

      <div class="privacy-notice">
        Displaying guest display_name and admitted_at only. No personal preferences, allergies, or identifiers shown.
      </div>
    </div>

    <!-- Local CV test card -->
    <div class="card">
      <h2>Face Recognition Test</h2>
      <div class="form-group">
        <label for="cv-device-token">Device token from local .env</label>
        <input type="password" id="cv-device-token" autocomplete="off" placeholder="DEVICE_AUTH_TOKEN" />
      </div>
      <div class="form-group">
        <label for="cv-device-id">Test device ID</label>
        <input type="text" id="cv-device-id" value="device-dashboard-test" autocomplete="off" spellcheck="false" />
      </div>
      <div class="form-group">
        <label for="cv-image-file">Choose a test picture</label>
        <input type="file" id="cv-image-file" accept="image/jpeg,image/png,image/webp" />
      </div>
      <img id="cv-image-preview" class="media-preview" alt="Selected test picture preview" hidden />
      <div class="cv-actions">
        <button type="button" class="btn-camera" id="cv-start-camera">Start camera</button>
        <button type="button" class="btn-secondary" id="cv-stop-camera" disabled>Stop camera</button>
      </div>
      <video id="cv-camera-preview" class="media-preview" autoplay playsinline muted hidden></video>
      <div class="cv-actions">
        <button type="button" class="btn-register" id="cv-send-picture" disabled>Send picture test</button>
        <button type="button" class="btn-register" id="cv-send-camera" disabled>Send 3 camera frames</button>
      </div>
      <div id="cv-feedback" class="feedback" role="status" aria-live="polite"></div>
      <div class="privacy-notice">
        Sends JPEG frames over the authenticated WebSocket on port 8000. Images are not saved. A still picture is replayed three times for a pipeline demo; use the camera burst for three distinct observations. Camera access requires localhost or HTTPS.
      </div>
    </div>
  </main>

  <script>
    const guestDropdown = document.getElementById('guest-dropdown');
    const guestRefInput = document.getElementById('guest-ref');
    const rosterTbody = document.getElementById('roster-tbody');
    const rosterEmpty = document.getElementById('roster-empty');
    const rosterCount = document.getElementById('roster-count');
    const tapFeedback = document.getElementById('tap-feedback');
    const registrationForm = document.getElementById('guest-registration-form');
    const registrationFeedback = document.getElementById('registration-feedback');
    const guestPhotoInput = document.getElementById('guest-photo-files');
    const guestPhotoCount = document.getElementById('guest-photo-count');
    const guestPhotoPreviews = document.getElementById('guest-photo-previews');
    const guestCameraVideo = document.getElementById('guest-camera-preview');
    const guestCameraStart = document.getElementById('guest-camera-start');
    const guestCameraCapture = document.getElementById('guest-camera-capture');
    const guestCameraStop = document.getElementById('guest-camera-stop');
    const sseDot = document.getElementById('sse-dot');
    const sseText = document.getElementById('sse-text');
    const cvTokenInput = document.getElementById('cv-device-token');
    const cvDeviceIdInput = document.getElementById('cv-device-id');
    const cvImageInput = document.getElementById('cv-image-file');
    const cvImagePreview = document.getElementById('cv-image-preview');
    const cvVideo = document.getElementById('cv-camera-preview');
    const cvFeedback = document.getElementById('cv-feedback');
    const cvStartCameraButton = document.getElementById('cv-start-camera');
    const cvStopCameraButton = document.getElementById('cv-stop-camera');
    const cvSendPictureButton = document.getElementById('cv-send-picture');
    const cvSendCameraButton = document.getElementById('cv-send-camera');
    let cvSelectedImage = null;
    let cvImageObjectUrl = null;
    let cvCameraStream = null;
    let cvSocket = null;
    let cvResolveCue = null;
    let cvRunActive = false;
    const registrationPhotos = [];
    let guestCameraStream = null;

    function showFeedback(message, type) {
      tapFeedback.textContent = message;
      tapFeedback.className = 'feedback ' + type;
    }

    function showCvFeedback(message, type) {
      cvFeedback.textContent = message;
      cvFeedback.className = 'feedback ' + type;
    }

    function refreshCvButtons() {
      const busy = cvRunActive;
      cvStartCameraButton.disabled = busy || Boolean(cvCameraStream);
      cvStopCameraButton.disabled = busy || !cvCameraStream;
      cvSendPictureButton.disabled = busy || !cvSelectedImage;
      cvSendCameraButton.disabled = busy || !cvCameraStream;
    }

    function handleCvMessage(message) {
      if (message.type === 'cue' && message.status === 'active') {
        const cue = message.cue || {};
        showCvFeedback([cue.headline, cue.alert].filter(Boolean).join(' · ') || 'Stable face match received.', 'success');
        if (cvResolveCue) cvResolveCue(message);
      } else if (message.type === 'clear') {
        showCvFeedback('Frames processed; no stable match yet. Check that Alex is admitted and the image matches the enrolled test face.', 'info');
      } else if (message.type === 'error') {
        showCvFeedback(message.message || 'The device stream reported an error.', 'error');
      }
    }

    function connectCvDevice(deviceId) {
      return new Promise((resolve, reject) => {
        const token = cvTokenInput.value.trim();
        if (!token) {
          reject(new Error('Enter DEVICE_AUTH_TOKEN from the local .env file.'));
          return;
        }
        if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/.test(deviceId)) {
          reject(new Error('Device ID must use letters, numbers, dot, underscore, or hyphen.'));
          return;
        }

        const scheme = location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${scheme}//${location.host}/v1/devices/${encodeURIComponent(deviceId)}/stream`;
        let settled = false;
        let timeoutId;
        let socket;
        try {
          socket = new WebSocket(url, ['device-stream-v1', `device-token.${token}`]);
        } catch (error) {
          reject(new Error(`Could not open device WebSocket: ${error.message}`));
          return;
        }
        cvSocket = socket;
        cvTokenInput.value = '';
        timeoutId = setTimeout(() => {
          if (!settled) {
            settled = true;
            socket.close();
            reject(new Error('Timed out waiting for lounge-control to authenticate the device.'));
          }
        }, 7000);

        socket.onmessage = event => {
          let message;
          try {
            message = JSON.parse(event.data);
          } catch (_) {
            return;
          }
          if (message.type === 'session_ack' && !settled) {
            settled = true;
            clearTimeout(timeoutId);
            resolve(socket);
          }
          handleCvMessage(message);
        };
        socket.onerror = () => {
          if (!settled) {
            settled = true;
            clearTimeout(timeoutId);
            reject(new Error('Could not connect. Check that the stack is running and reachable on port 8000.'));
          }
        };
        socket.onclose = event => {
          if (!settled) {
            settled = true;
            clearTimeout(timeoutId);
            reject(new Error(event.code === 1008 ? 'Device authentication failed. Check DEVICE_AUTH_TOKEN.' : 'Device connection closed before authentication.'));
          }
          if (cvSocket === socket) cvSocket = null;
        };
      });
    }

    function imageAsJpegBlob(image, maxBytes = 5 * 1024 * 1024) {
      return new Promise((resolve, reject) => {
        const width = image.videoWidth || image.naturalWidth;
        const height = image.videoHeight || image.naturalHeight;
        if (!width || !height) {
          reject(new Error('The selected image or camera has no usable frame.'));
          return;
        }
        const scale = Math.min(1, 1280 / width, 1280 / height);
        const canvas = document.createElement('canvas');
        canvas.width = Math.max(1, Math.round(width * scale));
        canvas.height = Math.max(1, Math.round(height * scale));
        const context = canvas.getContext('2d');
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(blob => {
          if (!blob) {
            reject(new Error('Could not encode this frame as JPEG.'));
          } else if (blob.size > maxBytes) {
            reject(new Error(`Encoded JPEG exceeds the ${Math.floor(maxBytes / (1024 * 1024))} MiB limit. Try a smaller image.`));
          } else {
            resolve(blob);
          }
        }, 'image/jpeg', 0.82);
      });
    }

    function delay(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }

    async function runCvFrames(frames, sourceLabel) {
      if (cvRunActive) return;
      cvRunActive = true;
      refreshCvButtons();
      let socket;
      let cuePromise;
      try {
        const deviceId = cvDeviceIdInput.value.trim();
        showCvFeedback('Connecting to lounge-control…', 'info');
        cuePromise = new Promise(resolve => { cvResolveCue = resolve; });
        socket = await connectCvDevice(deviceId);
        const streamId = `stream-ui-${Date.now()}`;
        for (let index = 0; index < frames.length; index += 1) {
          if (socket.readyState !== WebSocket.OPEN) throw new Error('Device connection closed before all frames were sent.');
          const metadata = {
            type: 'frame_meta',
            device_id: deviceId,
            stream_id: streamId,
            sequence: index + 1,
            captured_at: new Date().toISOString(),
            format: 'image/jpeg'
          };
          socket.send(JSON.stringify(metadata));
          socket.send(frames[index]);
          showCvFeedback(`Sent ${sourceLabel} frame ${index + 1}/${frames.length}; waiting for CV…`, 'info');
          if (index < frames.length - 1) await delay(600);
        }
        const result = await Promise.race([cuePromise, delay(15000).then(() => null)]);
        if (!result) {
          showCvFeedback('No stable match returned in 15 seconds. Confirm Alex is admitted and check face-worker logs.', 'info');
        }
      } catch (error) {
        showCvFeedback(error.message || 'The CV test could not run.', 'error');
      } finally {
        cvResolveCue = null;
        if (socket && socket.readyState === WebSocket.OPEN) socket.close(1000, 'CV test complete');
        cvRunActive = false;
        refreshCvButtons();
      }
    }

    cvImageInput.addEventListener('change', () => {
      const file = cvImageInput.files && cvImageInput.files[0];
      cvSelectedImage = null;
      if (cvImageObjectUrl) URL.revokeObjectURL(cvImageObjectUrl);
      cvImageObjectUrl = null;
      cvImagePreview.hidden = true;
      if (!file) {
        refreshCvButtons();
        return;
      }
      cvImageObjectUrl = URL.createObjectURL(file);
      const image = new Image();
      image.onload = () => {
        cvSelectedImage = image;
        cvImagePreview.src = cvImageObjectUrl;
        cvImagePreview.hidden = false;
        showCvFeedback(`Picture ready: ${file.name}. The pipeline test sends this still three times.`, 'info');
        refreshCvButtons();
      };
      image.onerror = () => showCvFeedback('Could not read the selected picture.', 'error');
      image.src = cvImageObjectUrl;
    });

    cvStartCameraButton.addEventListener('click', async () => {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showCvFeedback('Camera access needs localhost or an HTTPS page. On a phone, use the companion app or a trusted HTTPS setup.', 'error');
        return;
      }
      try {
        cvCameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
        cvVideo.srcObject = cvCameraStream;
        cvVideo.hidden = false;
        await cvVideo.play();
        showCvFeedback('Camera ready. Capture a three-frame burst when the test face is in view.', 'info');
      } catch (error) {
        cvCameraStream = null;
        showCvFeedback(`Could not start camera: ${error.message}`, 'error');
      }
      refreshCvButtons();
    });

    cvStopCameraButton.addEventListener('click', () => {
      if (cvCameraStream) cvCameraStream.getTracks().forEach(track => track.stop());
      cvCameraStream = null;
      cvVideo.srcObject = null;
      cvVideo.hidden = true;
      refreshCvButtons();
    });

    cvSendPictureButton.addEventListener('click', async () => {
      if (!cvSelectedImage) return;
      try {
        showCvFeedback('Preparing picture frames…', 'info');
        const frame = await imageAsJpegBlob(cvSelectedImage);
        await runCvFrames([frame, frame, frame], 'picture');
      } catch (error) {
        showCvFeedback(error.message, 'error');
      }
    });

    cvSendCameraButton.addEventListener('click', async () => {
      if (!cvCameraStream || !cvVideo.videoWidth) return;
      try {
        showCvFeedback('Capturing three distinct camera frames…', 'info');
        const frames = [];
        for (let index = 0; index < 3; index += 1) {
          frames.push(await imageAsJpegBlob(cvVideo));
          if (index < 2) await delay(700);
        }
        await runCvFrames(frames, 'camera');
      } catch (error) {
        showCvFeedback(error.message, 'error');
      }
    });

    refreshCvButtons();

    // Populate guest dropdown
    async function loadHotelGuests(selectedGuestRef = null) {
      try {
        const resp = await fetch('/v1/dashboard/guests');
        if (resp.ok) {
          const guests = await resp.json();
          guestDropdown.innerHTML = '<option value="">-- Choose guest or type reference below --</option>';
          guests.forEach(g => {
            const opt = document.createElement('option');
            opt.value = g.guest_ref;
            opt.textContent = `${g.display_name} (${g.guest_ref})`;
            guestDropdown.appendChild(opt);
          });
          const selectedRef = selectedGuestRef || guests[0]?.guest_ref || '';
          guestDropdown.value = selectedRef;
          if (selectedGuestRef || !guestRefInput.value) {
            guestRefInput.value = selectedRef;
          }
        }
      } catch (e) {
        console.warn('Failed to load hotel guests:', e);
      }
    }

    function showRegistrationFeedback(message, type) {
      registrationFeedback.textContent = message;
      registrationFeedback.className = 'feedback ' + type;
    }

    function commaSeparatedValues(value) {
      return value.split(',').map(item => item.trim()).filter(Boolean);
    }

    function updateGuestPhotoControls() {
      guestPhotoCount.textContent = `${registrationPhotos.length} of 3 photos selected`;
      guestCameraStart.disabled = Boolean(guestCameraStream) || registrationPhotos.length >= 3;
      guestCameraCapture.disabled = !guestCameraStream || registrationPhotos.length >= 3;
      guestCameraStop.disabled = !guestCameraStream;
      guestPhotoInput.disabled = registrationPhotos.length >= 3;
    }

    function renderGuestPhotoPreviews() {
      guestPhotoPreviews.querySelectorAll('img[data-object-url]').forEach(image => URL.revokeObjectURL(image.dataset.objectUrl));
      guestPhotoPreviews.replaceChildren();
      registrationPhotos.forEach((blob, index) => {
        const card = document.createElement('div');
        card.className = 'photo-card';
        const image = document.createElement('img');
        image.alt = `Guest reference photo ${index + 1}`;
        image.dataset.objectUrl = URL.createObjectURL(blob);
        image.src = image.dataset.objectUrl;
        const caption = document.createElement('span');
        caption.textContent = `Photo ${index + 1}`;
        const remove = document.createElement('button');
        remove.type = 'button';
        remove.className = 'photo-remove';
        remove.textContent = 'Remove';
        remove.setAttribute('aria-label', `Remove photo ${index + 1}`);
        remove.addEventListener('click', () => {
          registrationPhotos.splice(index, 1);
          renderGuestPhotoPreviews();
          updateGuestPhotoControls();
        });
        card.append(image, caption, remove);
        guestPhotoPreviews.appendChild(card);
      });
      updateGuestPhotoControls();
    }

    async function photoFileAsJpeg(file) {
      const objectUrl = URL.createObjectURL(file);
      try {
        const image = new Image();
        await new Promise((resolve, reject) => {
          image.onload = resolve;
          image.onerror = () => reject(new Error(`Could not read ${file.name} as an image.`));
          image.src = objectUrl;
        });
        return await imageAsJpegBlob(image, 2 * 1024 * 1024);
      } finally {
        URL.revokeObjectURL(objectUrl);
      }
    }

    function blobAsBase64(blob) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result).split(',')[1]);
        reader.onerror = () => reject(new Error('Could not encode a reference photo for upload.'));
        reader.readAsDataURL(blob);
      });
    }

    guestPhotoInput.addEventListener('change', async () => {
      const files = Array.from(guestPhotoInput.files || []);
      guestPhotoInput.value = '';
      const available = 3 - registrationPhotos.length;
      if (!files.length) return;
      const skippedCount = Math.max(0, files.length - available);
      try {
        for (const file of files.slice(0, available)) {
          registrationPhotos.push(await photoFileAsJpeg(file));
        }
        renderGuestPhotoPreviews();
        const skippedMessage = skippedCount ? ` ${skippedCount} extra photo${skippedCount === 1 ? '' : 's'} skipped; the limit is 3.` : '';
        showRegistrationFeedback(`${registrationPhotos.length} reference photo${registrationPhotos.length === 1 ? '' : 's'} ready.${skippedMessage}`, skippedCount ? 'info' : 'success');
      } catch (error) {
        renderGuestPhotoPreviews();
        showRegistrationFeedback(error.message, 'error');
      }
    });

    guestCameraStart.addEventListener('click', async () => {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showRegistrationFeedback('Live camera access needs localhost or HTTPS. You can also use the photo picker to take or upload images.', 'error');
        return;
      }
      try {
        guestCameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'user' } }, audio: false });
        guestCameraVideo.srcObject = guestCameraStream;
        guestCameraVideo.hidden = false;
        await guestCameraVideo.play();
        updateGuestPhotoControls();
        showRegistrationFeedback('Camera ready. Capture up to three distinct views.', 'info');
      } catch (error) {
        guestCameraStream = null;
        updateGuestPhotoControls();
        showRegistrationFeedback(`Could not start camera: ${error.message}`, 'error');
      }
    });

    guestCameraCapture.addEventListener('click', async () => {
      if (!guestCameraStream || !guestCameraVideo.videoWidth || registrationPhotos.length >= 3) return;
      guestCameraCapture.disabled = true;
      try {
        registrationPhotos.push(await imageAsJpegBlob(guestCameraVideo, 2 * 1024 * 1024));
        renderGuestPhotoPreviews();
        showRegistrationFeedback(`${registrationPhotos.length} reference photo${registrationPhotos.length === 1 ? '' : 's'} captured.`, 'success');
      } catch (error) {
        showRegistrationFeedback(error.message, 'error');
      } finally {
        updateGuestPhotoControls();
      }
    });

    guestCameraStop.addEventListener('click', () => {
      if (guestCameraStream) guestCameraStream.getTracks().forEach(track => track.stop());
      guestCameraStream = null;
      guestCameraVideo.srcObject = null;
      guestCameraVideo.hidden = true;
      updateGuestPhotoControls();
    });

    window.addEventListener('pagehide', () => {
      [guestCameraStream, cvCameraStream].filter(Boolean).forEach(stream => stream.getTracks().forEach(track => track.stop()));
    });

    async function registerGuest(event) {
      event.preventDefault();
      const displayName = document.getElementById('guest-name').value.trim();
      if (!displayName) {
        showRegistrationFeedback('Enter a guest name.', 'error');
        return;
      }

      const payload = {
        display_name: displayName,
        room_number: document.getElementById('guest-room').value.trim() || null,
        allergies: commaSeparatedValues(document.getElementById('guest-allergies').value),
        preferences: commaSeparatedValues(document.getElementById('guest-preferences').value),
        photos_b64: []
      };
      const button = document.getElementById('btn-register-guest');
      button.disabled = true;
      try {
        payload.photos_b64 = await Promise.all(registrationPhotos.map(blobAsBase64));
        const resp = await fetch('/v1/dashboard/guests', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || resp.statusText);
        registrationForm.reset();
        registrationPhotos.splice(0);
        renderGuestPhotoPreviews();
        if (guestCameraStream) guestCameraStream.getTracks().forEach(track => track.stop());
        guestCameraStream = null;
        guestCameraVideo.srcObject = null;
        guestCameraVideo.hidden = true;
        updateGuestPhotoControls();
        await loadHotelGuests(data.guest_ref);
        const photoMessage = payload.photos_b64.length
          ? `${payload.photos_b64.length} reference photo${payload.photos_b64.length === 1 ? '' : 's'} saved.`
          : 'No face reference photos were saved; the generated placeholder will not match a live face.';
        showRegistrationFeedback(
          `Registered ${data.display_name}. Guest reference: ${data.guest_ref}. ${photoMessage}`,
          payload.photos_b64.length ? 'success' : 'info'
        );
      } catch (err) {
        showRegistrationFeedback(`Could not register guest: ${err.message}`, 'error');
      } finally {
        button.disabled = false;
      }
    }

    registrationForm.addEventListener('submit', registerGuest);

    guestDropdown.addEventListener('change', (e) => {
      if (e.target.value) {
        guestRefInput.value = e.target.value;
      }
    });

    // Fetch and render active roster
    async function fetchRoster() {
      try {
        const resp = await fetch('/v1/lounge/roster');
        if (!resp.ok) throw new Error('Status ' + resp.status);
        const roster = await resp.json();
        renderRoster(roster);
      } catch (e) {
        console.error('Failed to fetch roster:', e);
      }
    }

    function renderRoster(roster) {
      rosterTbody.innerHTML = '';
      rosterCount.textContent = roster.length;
      if (!roster || roster.length === 0) {
        rosterEmpty.style.display = 'block';
        return;
      }
      rosterEmpty.style.display = 'none';
      roster.forEach(entry => {
        const row = document.createElement('tr');
        const nameCell = document.createElement('td');
        nameCell.textContent = entry.display_name;
        nameCell.style.fontWeight = '500';

        const admittedCell = document.createElement('td');
        let formattedTime = entry.admitted_at;
        try {
          const d = new Date(entry.admitted_at);
          formattedTime = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        } catch (_) {}
        admittedCell.textContent = formattedTime;
        admittedCell.style.color = 'var(--text-muted)';

        row.appendChild(nameCell);
        row.appendChild(admittedCell);
        rosterTbody.appendChild(row);
      });
    }

    // Submit tap event
    async function submitTap(eventType) {
      const guestRef = guestRefInput.value.trim();
      if (!guestRef) {
        showFeedback('Please select or enter a guest reference.', 'error');
        return;
      }

      const eventId = 'evt-dash-' + Math.random().toString(36).substring(2, 10);
      const payload = {
        event_id: eventId,
        reader_id: 'lounge-laptop-dashboard',
        guest_ref: guestRef,
        event_type: eventType,
        occurred_at: new Date().toISOString()
      };

      try {
        const resp = await fetch('/v1/lounge/taps', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (resp.ok) {
          if (data.action === 'already_admitted') {
            showFeedback(`Guest '${guestRef}' is already admitted. Single presence preserved.`, 'info');
          } else if (data.action === 'admitted') {
            showFeedback(`Guest '${guestRef}' admitted successfully.`, 'success');
          } else if (data.action === 'departed') {
            const count = (data.removed_candidates || []).length;
            showFeedback(`Guest '${guestRef}' departed (${count} presence removed).`, 'success');
          } else {
            showFeedback(`Tap recorded: ${JSON.stringify(data)}`, 'success');
          }
          fetchRoster();
        } else {
          showFeedback(`Tap error: ${data.detail || resp.statusText}`, 'error');
        }
      } catch (err) {
        showFeedback(`Network error submitting tap: ${err.message}`, 'error');
      }
    }

    // Connect to Server-Sent Events (SSE)
    function connectSSE() {
      const evtSource = new EventSource('/v1/lounge/events');

      evtSource.addEventListener('connected', () => {
        sseDot.className = 'status-dot connected';
        sseText.textContent = 'SSE Live';
      });

      evtSource.addEventListener('roster_change', (e) => {
        fetchRoster();
      });

      evtSource.onopen = () => {
        sseDot.className = 'status-dot connected';
        sseText.textContent = 'SSE Live';
        fetchRoster();
      };

      evtSource.onerror = () => {
        sseDot.className = 'status-dot';
        sseText.textContent = 'SSE Reconnecting...';
      };
    }

    // Initialize
    loadHotelGuests();
    fetchRoster();
    connectSSE();
  </script>
</body>
</html>
"""
