package com.example.rokid_app

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.ImageFormat
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.util.Log
import android.util.Size
import android.view.Surface
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.ImageProxy
import androidx.camera.core.resolutionselector.ResolutionSelector
import androidx.camera.core.resolutionselector.ResolutionStrategy
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import java.util.Locale
import java.util.UUID
import java.util.concurrent.Executors

/** Camera capture and server results only: no local ML or visible camera preview. */
class MainActivity : AppCompatActivity() {
    private lateinit var statusText: TextView
    private lateinit var client: FaceServerClient
    private val handler = Handler(Looper.getMainLooper())
    private val ioExecutor = Executors.newSingleThreadExecutor()
    private var provider: ProcessCameraProvider? = null
    private var capture: ImageCapture? = null
    @Volatile private var session = 0
    @Volatile private var active = false
    private var busy = false
    private var connected = false
    private var nextRequestAt = 0L

    private val permissionRequest = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted && active) startCamera(session)
        else if (!granted) showStatus("Camera permission is required.\nEnable it in app settings.")
    }

    private val tick = object : Runnable {
        override fun run() {
            if (!active) return
            if (!busy && capture != null && SystemClock.elapsedRealtime() >= nextRequestAt) {
                nextRequestAt = SystemClock.elapsedRealtime() + CAPTURE_INTERVAL_MS
                if (connected) captureAndSend(session) else checkConnection(session)
            }
            handler.postDelayed(this, CAPTURE_INTERVAL_MS)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        statusText = findViewById(R.id.statusText)
        client = FaceServerClient(BuildConfig.FACE_SERVER_URL)
        WindowCompat.getInsetsController(window, window.decorView).apply {
            systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            hide(WindowInsetsCompat.Type.systemBars())
        }
        if (!hasCameraPermission()) permissionRequest.launch(Manifest.permission.CAMERA)
    }

    override fun onStart() {
        super.onStart()
        client.resume()
        active = true
        session++
        busy = false
        connected = false
        nextRequestAt = 0
        showStatus("Connecting to server...")
        if (hasCameraPermission()) startCamera(session)
        handler.post(tick)
    }

    private fun hasCameraPermission() =
        ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED

    private fun isCurrent(token: Int) = active && token == session

    private fun startCamera(token: Int) {
        val future = ProcessCameraProvider.getInstance(this)
        future.addListener({
            if (!isCurrent(token) || capture != null) return@addListener
            try {
                val cameraProvider = future.get()
                provider = cameraProvider
                val selector = when {
                    cameraProvider.hasCamera(CameraSelector.DEFAULT_BACK_CAMERA) -> CameraSelector.DEFAULT_BACK_CAMERA
                    cameraProvider.hasCamera(CameraSelector.DEFAULT_FRONT_CAMERA) -> CameraSelector.DEFAULT_FRONT_CAMERA
                    else -> error("No camera available")
                }
                val imageCapture = ImageCapture.Builder()
                    .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                    .setJpegQuality(80)
                    .setResolutionSelector(
                        ResolutionSelector.Builder().setResolutionStrategy(
                            ResolutionStrategy(Size(1280, 960), ResolutionStrategy.FALLBACK_RULE_CLOSEST_HIGHER_THEN_LOWER)
                        ).build()
                    )
                    .setTargetRotation(statusText.display?.rotation ?: Surface.ROTATION_0)
                    .build()
                // No Preview, ImageAnalysis, crop ratio, or ViewPort. Send the whole captured JPEG.
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(this, selector, imageCapture)
                capture = imageCapture
            } catch (error: Exception) {
                Log.e(TAG, "Camera startup failed", error)
                showStatus("Unable to start camera.\nClose and reopen the app.")
            }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun checkConnection(token: Int) {
        busy = true
        ioExecutor.execute {
            if (!isCurrent(token)) return@execute
            val result = runCatching { client.checkHealth() }
            handler.post {
                if (!isCurrent(token)) return@post
                busy = false
                connected = result.isSuccess
                if (connected) {
                    showStatus("Connected to server")
                    nextRequestAt = SystemClock.elapsedRealtime() + CAPTURE_INTERVAL_MS
                } else {
                    Log.w(TAG, "Server unavailable", result.exceptionOrNull())
                    showStatus("Server unavailable. Retrying...")
                }
            }
        }
    }

    private fun captureAndSend(token: Int) {
        val imageCapture = capture ?: return
        busy = true
        val requestId = UUID.randomUUID().toString()
        imageCapture.targetRotation = statusText.display?.rotation ?: Surface.ROTATION_0
        val captureStartedNs = SystemClock.elapsedRealtimeNanos()
        imageCapture.takePicture(ioExecutor, object : ImageCapture.OnImageCapturedCallback() {
            override fun onCaptureSuccess(image: ImageProxy) {
                var rotation = 0
                val jpeg = try {
                    if (!isCurrent(token)) return
                    check(image.format == ImageFormat.JPEG) { "Camera did not return JPEG" }
                    rotation = image.imageInfo.rotationDegrees
                    val buffer = image.planes[0].buffer
                    check(buffer.remaining() <= FaceServerClient.MAX_IMAGE_BYTES) { "Camera image is too large" }
                    ByteArray(buffer.remaining()).also { buffer.get(it) }
                } catch (error: Exception) {
                    finishCaptureFailure(token, error)
                    return
                } finally {
                    image.close()
                }
                if (!isCurrent(token)) return
                val jpegReadyNs = SystemClock.elapsedRealtimeNanos()
                // JPEG rotation is handled by the server. No bitmap conversion or cropping on glasses.
                val result = runCatching { client.detect(jpeg, rotation, requestId) }
                val responseReceivedNs = SystemClock.elapsedRealtimeNanos()
                handler.post {
                    if (!isCurrent(token)) return@post
                    busy = false
                    result.onSuccess { response ->
                        showStatus(response.display)
                        val uiUpdatedNs = SystemClock.elapsedRealtimeNanos()
                        Log.i("FaceLatency", String.format(
                            Locale.US,
                            "request_id=%s capture_ms=%.1f http_ms=%.1f inference_ms=%.1f capture_to_response_ms=%.1f capture_to_ui_ms=%.1f jpeg_bytes=%d face_count=%d",
                            requestId,
                            (jpegReadyNs - captureStartedNs) / 1_000_000.0,
                            (responseReceivedNs - jpegReadyNs) / 1_000_000.0,
                            response.inferenceMs,
                            (responseReceivedNs - captureStartedNs) / 1_000_000.0,
                            (uiUpdatedNs - captureStartedNs) / 1_000_000.0,
                            jpeg.size, response.faceCount
                        ))
                    }.onFailure {
                        connected = false
                        showStatus("Server unavailable. Retrying...")
                        Log.w(TAG, "Upload or detection failed", it)
                    }
                }
            }

            override fun onError(exception: ImageCaptureException) {
                finishCaptureFailure(token, exception)
            }
        })
    }

    private fun finishCaptureFailure(token: Int, error: Exception) {
        Log.w(TAG, "Capture failed", error)
        handler.post {
            if (isCurrent(token)) {
                busy = false
                showStatus("Camera capture failed. Retrying...")
            }
        }
    }

    private fun showStatus(text: String) {
        if (statusText.text.toString() != text) statusText.text = text
    }

    override fun onStop() {
        active = false
        session++
        handler.removeCallbacksAndMessages(null)
        client.cancel()
        provider?.unbindAll()
        capture = null
        super.onStop()
    }

    override fun onDestroy() {
        client.close()
        ioExecutor.shutdownNow()
        super.onDestroy()
    }

    companion object {
        private const val TAG = "FaceCamera"
        private const val CAPTURE_INTERVAL_MS = 2_000L
    }
}
