package com.example.rokid_app

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.util.Log
import android.util.Size
import android.view.KeyEvent
import android.view.Surface
import android.view.View
import android.widget.LinearLayout
import android.widget.SeekBar
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.CameraSelector
import androidx.camera.core.ExperimentalGetImage
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.core.resolutionselector.ResolutionSelector
import androidx.camera.core.resolutionselector.ResolutionStrategy
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.face.FaceDetection
import com.google.mlkit.vision.face.FaceDetectorOptions
import java.util.UUID
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.CancellationException

class MainActivity : AppCompatActivity() {
    private lateinit var statusText: TextView
    private lateinit var serverStatus: ServerStatusView
    private lateinit var overlay: FaceOverlayView
    private lateinit var client: FaceServerClient
    private val handler = Handler(Looper.getMainLooper())
    private val analysisExecutor = Executors.newSingleThreadExecutor()
    private val ioExecutor = Executors.newSingleThreadExecutor()
    private val detector = FaceDetection.getClient(FaceDetectorOptions.Builder()
        .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST).enableTracking().build())
    private val tracking = FaceTracking()
    private val requestBusy = AtomicBoolean(false)
    private var provider: ProcessCameraProvider? = null
    private var analysis: ImageAnalysis? = null
    @Volatile private var session = 0
    @Volatile private var active = false
    @Volatile private var connected = false
    @Volatile private var interaction = InteractionWindow()
    private var lastForwardAt = -1_000L
    private var firstDetectionAt = 0L
    private var lastAnalysisAt = 0L
    private var lastTrackingLogAt = 0L
    @Volatile private var nextRequestAt = 0L
    private var geometry = ""
    private var lastFrameAt = 0L
    private var calibrationDialog: AlertDialog? = null
    // Accessed only on analysisExecutor, including shutdown after outstanding ML work.
    private var pendingFrames = 0
    private var closing = false

    private val permissionRequest = registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted && active && interaction.detecting(SystemClock.elapsedRealtime())) startCamera(session)
        else if (!granted && active && interaction.detecting(SystemClock.elapsedRealtime()))
            showStatus("Camera permission is required.")
    }
    private val heartbeat = object : Runnable {
        override fun run() {
            if (!active) return
            if (SystemClock.elapsedRealtime() - lastFrameAt > 500) { tracking.clear(); overlay.clear() }
            if (requestBusy.compareAndSet(false, true)) checkConnection(session)
            handler.postDelayed(this, 2_000)
        }
    }
    private val detectionTimeout = Runnable { endDetection() }
    private val statusTimeout = Runnable { serverStatus.visibility = View.GONE }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContentView(R.layout.activity_main)
        statusText = findViewById(R.id.statusText)
        serverStatus = findViewById(R.id.serverStatus)
        serverStatus.visibility = View.GONE
        overlay = findViewById(R.id.faceOverlay)
        // Debug-only USB transport for testing when Wi-Fi clients cannot reach each other.
        val serverUrl = if (BuildConfig.DEBUG && intent.getBooleanExtra("usb_server", false))
            "http://127.0.0.1:8000" else BuildConfig.FACE_SERVER_URL
        client = FaceServerClient(serverUrl)
        val prefs = getSharedPreferences("label_calibration", MODE_PRIVATE)
        overlay.calibration = LabelCalibration(prefs.getFloat("sx", 1f), prefs.getFloat("sy", 1f),
            prefs.getFloat("ox", 0f), prefs.getFloat("oy", 0f))
        overlay.setOnClickListener { beginDetection() }
        overlay.setOnLongClickListener { if (BuildConfig.DEBUG) openCalibration(); true }
        WindowCompat.getInsetsController(window, window.decorView).apply {
            systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            hide(WindowInsetsCompat.Type.systemBars())
        }
        if (!hasCameraPermission()) permissionRequest.launch(Manifest.permission.CAMERA)
        applyControls(intent)
        warmDetector()
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        applyControls(intent)
    }

    override fun onStart() {
        super.onStart()
        client.resume(); active = true; session++; connected = false
        interaction = InteractionWindow()
        serverStatus.state = ServerStatusView.State.CONNECTING
        serverStatus.visibility = View.GONE
        showStatus("")
        // Initialize CameraX once without opening a camera during idle.
        ProcessCameraProvider.getInstance(this)
        handler.post(heartbeat)
    }

    private fun hasCameraPermission() = ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
    private fun isCurrent(token: Int) = active && token == session
    private fun isScanning(token: Int, scanId: Long) = isCurrent(token) &&
        interaction.acceptsResult(scanId, SystemClock.elapsedRealtime())

    private fun beginDetection() {
        if (!active) return
        val now = SystemClock.elapsedRealtime()
        interaction = interaction.tap(now)
        client.setDetectionScan(interaction.scanId)
        firstDetectionAt = 0
        nextRequestAt = 0
        tracking.clear(); overlay.clear(); showStatus("")
        handler.removeCallbacks(detectionTimeout)
        handler.postDelayed(detectionTimeout, InteractionWindow.DETECTION_MS)
        Log.i("FaceInteraction", "detection_started scan_id=${interaction.scanId} duration_ms=${InteractionWindow.DETECTION_MS}")
        if (hasCameraPermission()) startCamera(session)
        else permissionRequest.launch(Manifest.permission.CAMERA)
    }

    private fun endDetection() {
        interaction = interaction.stopDetection()
        client.setDetectionScan(null)
        handler.removeCallbacks(detectionTimeout)
        analysis?.clearAnalyzer(); provider?.unbindAll(); analysis = null
        tracking.clear(); overlay.clear(); showStatus("")
        Log.i("FaceInteraction", "detection_stopped")
        // Keep health checks alive, but cancel recognition uploads from the expired scan.
    }

    private fun revealServerStatus() {
        if (!active) return
        val now = SystemClock.elapsedRealtime()
        if (now - lastForwardAt < 250) return // Some firmware emits two direction keys per swipe.
        lastForwardAt = now
        interaction = interaction.swipeForward(now)
        serverStatus.visibility = View.VISIBLE
        handler.removeCallbacks(statusTimeout)
        handler.postDelayed(statusTimeout, InteractionWindow.STATUS_MS)
        Log.i("FaceInteraction", "status_shown state=${serverStatus.state}")
    }

    private fun warmDetector() {
        analysisExecutor.execute {
            val bitmap = Bitmap.createBitmap(128, 128, Bitmap.Config.ARGB_8888)
            pendingFrames++
            try {
                detector.process(InputImage.fromBitmap(bitmap, 0)).addOnCompleteListener(analysisExecutor) {
                    if (!it.isSuccessful) Log.w(TAG, "Detector warmup failed", it.exception)
                    bitmap.recycle(); pendingFrames--; closeDetectorIfIdle()
                }
            } catch (error: Exception) {
                bitmap.recycle(); pendingFrames--; closeDetectorIfIdle()
                Log.w(TAG, "Detector warmup failed", error)
            }
        }
    }

    private fun startCamera(token: Int) {
        val scanId = interaction.scanId
        val future = ProcessCameraProvider.getInstance(this)
        future.addListener({
            if (!isScanning(token, scanId) || analysis != null) return@addListener
            try {
                val cameraProvider = future.get()
                provider = cameraProvider
                check(cameraProvider.hasCamera(CameraSelector.DEFAULT_BACK_CAMERA)) { "No outward camera" }
                val stream = ImageAnalysis.Builder()
                    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                    .setResolutionSelector(ResolutionSelector.Builder().setResolutionStrategy(
                        ResolutionStrategy(Size(960, 720), ResolutionStrategy.FALLBACK_RULE_CLOSEST_HIGHER_THEN_LOWER)
                    ).build())
                    .setTargetRotation(overlay.display?.rotation ?: Surface.ROTATION_0).build()
                stream.setAnalyzer(analysisExecutor) { analyze(it, token) }
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(this, CameraSelector.DEFAULT_BACK_CAMERA, stream)
                analysis = stream
            } catch (error: Exception) {
                Log.e(TAG, "Camera startup failed", error)
                showStatus("Unable to start outward camera.")
            }
        }, ContextCompat.getMainExecutor(this))
    }

    @androidx.annotation.OptIn(ExperimentalGetImage::class)
    private fun analyze(image: ImageProxy, token: Int) {
        val started = SystemClock.elapsedRealtime()
        val scanId = interaction.scanId
        if (!isScanning(token, scanId) || started - lastAnalysisAt < 80) { image.close(); return }
        lastAnalysisAt = started
        val media = image.image
        if (media == null) { image.close(); return }
        val rotation = image.imageInfo.rotationDegrees
        val width = if (rotation % 180 == 0) image.width else image.height
        val height = if (rotation % 180 == 0) image.height else image.width
        try {
            pendingFrames++
            detector.process(InputImage.fromMediaImage(media, rotation))
                .addOnCompleteListener(analysisExecutor) { task ->
                    try {
                        if (!isScanning(token, scanId)) return@addOnCompleteListener
                        val faces = task.result.mapNotNull { face ->
                            val id = face.trackingId ?: return@mapNotNull null
                            val box = face.boundingBox
                            id to FaceBox(box.left.toFloat() / width, box.top.toFloat() / height,
                                box.right.toFloat() / width, box.bottom.toFloat() / height)
                        }
                        val detectedAt = SystemClock.elapsedRealtime()
                        val focused = focusedFace(faces, overlay.calibration)
                        var jpeg: RecognitionFrame? = null
                        if (focused != null && connected && interaction.canStartRecognition(detectedAt) && started >= nextRequestAt && requestBusy.compareAndSet(false, true)) {
                            try { jpeg = cameraJpeg(image, focused.second); nextRequestAt = started + 2_000 }
                            catch (error: Exception) { requestBusy.set(false); throw error }
                        }
                        val payload = jpeg
                        val encodedAt = SystemClock.elapsedRealtime()
                        handler.post {
                            if (!isScanning(token, scanId)) {
                                if (payload != null) requestBusy.set(false)
                                return@post
                            }
                            val now = SystemClock.elapsedRealtime()
                            if (firstDetectionAt == 0L) {
                                firstDetectionAt = now
                                Log.i("FaceInteraction", "first_analysis_ms=${now - (interaction.detectionUntil - InteractionWindow.DETECTION_MS)} scan_id=$scanId")
                            }
                            val frameGeometry = "$width:$height:$rotation"
                            if (geometry != frameGeometry || now - lastFrameAt > 500) tracking.clear()
                            geometry = frameGeometry; lastFrameAt = now
                            val snapshot = tracking.update(faces, setOfNotNull(focused?.first))
                            overlay.show(tracking.labels(now, overlay.debug), snapshot.map { it.box })
                            if (now - lastTrackingLogAt >= 2_000) {
                                lastTrackingLogAt = now
                                Log.i("FaceTracking", "analysis_ms=${now - started} detector_ms=${detectedAt - started} jpeg_ms=${encodedAt - detectedAt} tracks=${faces.size} focused=${snapshot.size} ids=${snapshot.map { it.id }} upright=${width}x$height rotation=$rotation")
                            }
                            if (connected) showStatus("")
                            if (payload != null) recognize(payload, rotation, snapshot, started, token, scanId)
                        }
                    } catch (error: Exception) {
                        Log.w(TAG, "Frame analysis failed", error)
                        handler.post { if (isScanning(token, scanId)) { tracking.clear(); overlay.clear(); showStatus("Face tracking unavailable. Retrying...") } }
                    } finally { image.close(); pendingFrames--; closeDetectorIfIdle() }
                }
        } catch (error: Exception) {
            image.close(); pendingFrames--; closeDetectorIfIdle()
            Log.w(TAG, "Detector failed", error)
        }
    }

    private fun recognize(frame: RecognitionFrame, rotation: Int, snapshot: List<TrackedFace>, started: Long, token: Int, scanId: Long) {
        ioExecutor.execute {
            if (!isScanning(token, scanId) || !interaction.canStartRecognition(SystemClock.elapsedRealtime())) {
                requestBusy.set(false); return@execute
            }
            val requestId = UUID.randomUUID().toString()
            val httpStarted = SystemClock.elapsedRealtime()
            val deadlineAt = interaction.detectionUntil
            Log.i("FaceLatency", "request_started id=$requestId scan_id=$scanId remaining_ms=${deadlineAt - httpStarted} jpeg_bytes=${frame.jpeg.size}")
            val result = runCatching { check(isCurrent(token)); client.detect(frame.jpeg, rotation, requestId, scanId, deadlineAt) }
            val responseAt = SystemClock.elapsedRealtime()
            handler.post {
                requestBusy.set(false)
                if (!isCurrent(token)) return@post
                result.onSuccess { response ->
                    connected = true
                    serverStatus.state = ServerStatusView.State.ONLINE
                    if (!isScanning(token, scanId)) return@onSuccess
                    val now = SystemClock.elapsedRealtime()
                    val faces = response.faces.map { it.copy(box = it.box.within(frame.uprightRegion)) }
                    tracking.recognize(snapshot, faces, started, now)
                    Log.i("FaceLatency", "request_id=$requestId scan_id=$scanId frame_to_response_ms=${now - started} http_ms=${responseAt - httpStarted} inference_ms=${response.inferenceMs} face_count=${response.faceCount}")
                }.onFailure { error ->
                    if (error is CancellationException || !isScanning(token, scanId)) {
                        Log.i("FaceLatency", "request_cancelled id=$requestId scan_id=$scanId")
                        return@onFailure
                    }
                    connected = false
                    if (isScanning(token, scanId)) { tracking.clearNames(); overlay.clear() }
                    serverStatus.state = ServerStatusView.State.OFFLINE
                    Log.w(TAG, "Recognition failed", error)
                }
            }
        }
    }

    private fun checkConnection(token: Int) {
        ioExecutor.execute {
            val result = runCatching { check(isCurrent(token)); client.checkHealth() }
            handler.post {
                requestBusy.set(false)
                if (!isCurrent(token)) return@post
                connected = result.isSuccess
                Log.i("FaceConnection", "health=${if (connected) "online" else "offline"} scanning=${interaction.detecting(SystemClock.elapsedRealtime())}")
                serverStatus.state = if (connected) ServerStatusView.State.ONLINE else ServerStatusView.State.OFFLINE
                if (!connected) { tracking.clearNames(); overlay.clear() }
                if (!connected) Log.w(TAG, "Server health check failed", result.exceptionOrNull())
            }
        }
    }

    private fun showStatus(text: String) { statusText.text = text }

    private fun applyControls(intent: Intent) {
        if (intent.hasExtra("debug")) overlay.debug = intent.getBooleanExtra("debug", false)
        fun value(key: String, fallback: Float, low: Float, high: Float): Float {
            val number = intent.getFloatExtra(key, fallback)
            return if (number.isFinite()) number.coerceIn(low, high) else fallback
        }
        val c = overlay.calibration
        overlay.calibration = LabelCalibration(value("scale_x", c.scaleX, 0.1f, 12f),
            value("scale_y", c.scaleY, 0.1f, 12f), value("offset_x", c.offsetX, -2f, 2f), value("offset_y", c.offsetY, -2f, 2f))
        if (listOf("scale_x", "scale_y", "offset_x", "offset_y").any { intent.hasExtra(it) }) saveCalibration()
        if (BuildConfig.DEBUG && intent.getBooleanExtra("calibration", false)) overlay.post { openCalibration() }
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        if (BuildConfig.DEBUG && keyCode == KeyEvent.KEYCODE_MENU) { openCalibration(); return true }
        return super.onKeyDown(keyCode, event)
    }

    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        if (calibrationDialog?.isShowing == true) return super.dispatchKeyEvent(event)
        if (event.keyCode == KeyEvent.KEYCODE_NOTIFICATION) return true
        val tap = event.keyCode == KeyEvent.KEYCODE_ENTER || event.keyCode == KeyEvent.KEYCODE_DPAD_CENTER
        val forward = event.keyCode == KeyEvent.KEYCODE_DPAD_RIGHT || event.keyCode == KeyEvent.KEYCODE_DPAD_DOWN || event.scanCode == 183
        if (tap || forward) {
            if (event.action == KeyEvent.ACTION_UP && !event.isCanceled) {
                Log.i("FaceInteraction", "key=${event.keyCode} scan=${event.scanCode} device=${event.device?.name}")
                if (tap) beginDetection() else revealServerStatus()
            }
            return true
        }
        return super.dispatchKeyEvent(event)
    }

    private fun openCalibration() {
        if (calibrationDialog?.isShowing == true) return
        beginDetection()
        overlay.debug = true
        val initial = overlay.calibration
        val container = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(16, 0, 16, 0) }
        fun slider(title: String, initialValue: Float, minimum: Float, maximum: Float, change: (Float) -> Unit) {
            val label = TextView(this)
            container.addView(label)
            val seek = SeekBar(this).apply { max = 200; progress = ((initialValue - minimum) / (maximum - minimum) * 200).toInt() }
            fun update(value: Int) {
                val number = minimum + value / 200f * (maximum - minimum)
                label.text = String.format(java.util.Locale.US, "%s: %.2f", title, number)
                change(number)
            }
            label.text = String.format(java.util.Locale.US, "%s: %.2f", title, initialValue)
            seek.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) { if (fromUser) update(progress) }
                override fun onStartTrackingTouch(seekBar: SeekBar?) {}
                override fun onStopTrackingTouch(seekBar: SeekBar?) {}
            })
            container.addView(seek)
        }
        slider("Horizontal scale", initial.scaleX, 0.1f, 12f) { overlay.calibration = overlay.calibration.copy(scaleX = it) }
        slider("Vertical scale", initial.scaleY, 0.1f, 12f) { overlay.calibration = overlay.calibration.copy(scaleY = it) }
        slider("Horizontal offset", initial.offsetX, -2f, 2f) { overlay.calibration = overlay.calibration.copy(offsetX = it) }
        slider("Vertical offset", initial.offsetY, -2f, 2f) { overlay.calibration = overlay.calibration.copy(offsetY = it) }
        calibrationDialog = AlertDialog.Builder(this).setTitle("Label alignment")
            .setView(container)
            .setPositiveButton("Save") { _, _ -> saveCalibration() }
            .setNeutralButton("Reset") { _, _ -> overlay.calibration = LabelCalibration(); saveCalibration() }
            .setNegativeButton("Cancel") { _, _ -> overlay.calibration = initial; overlay.debug = false }
            .create().apply {
                setOnCancelListener { overlay.calibration = initial; overlay.debug = false }
                setOnDismissListener { calibrationDialog = null }
                show()
            }
    }

    private fun saveCalibration() {
        val c = overlay.calibration
        getSharedPreferences("label_calibration", MODE_PRIVATE).edit()
            .putFloat("sx", c.scaleX).putFloat("sy", c.scaleY).putFloat("ox", c.offsetX).putFloat("oy", c.offsetY).apply()
    }

    override fun onStop() {
        active = false; session++
        interaction = InteractionWindow()
        client.setDetectionScan(null)
        handler.removeCallbacks(heartbeat)
        handler.removeCallbacks(detectionTimeout)
        handler.removeCallbacks(statusTimeout)
        serverStatus.visibility = View.GONE
        client.cancel()
        analysis?.clearAnalyzer(); provider?.unbindAll(); analysis = null
        tracking.clear(); overlay.clear()
        calibrationDialog?.dismiss()
        super.onStop()
    }

    override fun onDestroy() {
        client.close()
        analysisExecutor.execute { closing = true; closeDetectorIfIdle() }
        ioExecutor.shutdown()
        super.onDestroy()
    }

    private fun closeDetectorIfIdle() {
        if (closing && pendingFrames == 0) { detector.close(); analysisExecutor.shutdown() }
    }

    companion object { private const val TAG = "FaceCamera" }
}
