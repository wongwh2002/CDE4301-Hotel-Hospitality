package com.example.rokid_app

import org.json.JSONObject
import android.os.SystemClock
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.CancellationException

data class FaceServerResult(val display: String, val inferenceMs: Double, val faces: List<NamedFace>) {
    val faceCount get() = faces.size
}

/** Small HTTP client; called only on the I/O executor. */
class FaceServerClient(baseUrl: String) {
    private val lock = Any()
    private var enabled = true
    private val base = baseUrl.trimEnd('/')
    private val timeoutExecutor = Executors.newSingleThreadScheduledExecutor()
    @Volatile private var connection: HttpURLConnection? = null
    private var activeScanId: Long? = null
    private var activeScanDeadlineAt: Long? = null
    private var connectionScanId: Long? = null

    fun checkHealth() {
        val response = request("/health")
        check(response.optString("status") == "ready" && response.optInt("protocol_version") == PROTOCOL_VERSION) {
            "Incompatible or unready server"
        }
    }

    fun detect(jpeg: ByteArray, rotation: Int, requestId: String, scanId: Long, deadlineAt: Long): FaceServerResult {
        val response = request("/detect?rotation=$rotation&request_id=$requestId", jpeg, scanId, deadlineAt)
        check(response.getString("request_id") == requestId) { "Response ID mismatch" }
        check(response.getInt("protocol_version") == PROTOCOL_VERSION) { "Incompatible server" }
        val width = response.getInt("image_width").also { check(it > 0) }.toFloat()
        val height = response.getInt("image_height").also { check(it > 0) }.toFloat()
        val array = response.getJSONArray("faces")
        val faces = (0 until array.length()).map { index ->
            val face = array.getJSONObject(index)
            val box = face.getJSONObject("box")
            val x = box.getInt("x"); val y = box.getInt("y")
            val w = box.getInt("width"); val h = box.getInt("height")
            check(x >= 0 && y >= 0 && w > 0 && h > 0 && x.toLong() + w <= width && y.toLong() + h <= height)
            val name = face.getString("name").take(80).ifBlank { "Unknown" }
            val cues = if (name.trim().equals("Unknown", true)) emptyList() else {
                val items = face.optJSONArray("cues")
                (0 until minOf(items?.length() ?: 0, 2)).mapNotNull { cueIndex ->
                    val cue = items?.optJSONObject(cueIndex) ?: return@mapNotNull null
                    GuestCue(cue.optString("code"), cue.optString("sentiment"))
                        .takeIf { GuestCueIcons.icon(it.code) != null && GuestCueIcons.marker(it.sentiment) != null }
                }
            }
            NamedFace(name, FaceBox(x / width, y / height, (x + w) / width, (y + h) / height), cues)
        }
        return FaceServerResult(
            response.getString("display").take(500).ifBlank { "Unknown" },
            response.optDouble("inference_ms", Double.NaN),
            faces
        )
    }

    private fun request(path: String, jpeg: ByteArray? = null, scanId: Long? = null, deadlineAt: Long? = null): JSONObject {
        val conn = synchronized(lock) {
            check(enabled) { "Client stopped" }
            if (scanId != null) {
                if (scanId != activeScanId) throw CancellationException("Detection window ended")
                activeScanDeadlineAt = maxOf(activeScanDeadlineAt ?: deadlineAt!!, deadlineAt!!)
                if (SystemClock.elapsedRealtime() >= activeScanDeadlineAt!!) throw CancellationException("Detection window ended")
            }
            (URL(base + path).openConnection() as HttpURLConnection).also { connection = it; connectionScanId = scanId }
        }
        val requestLimit = SystemClock.elapsedRealtime() + 12_000L
        fun scanExpired() = scanId != null && synchronized(lock) {
            activeScanId != scanId || SystemClock.elapsedRealtime() >= (activeScanDeadlineAt ?: deadlineAt!!)
        }
        // Re-read the shared deadline: speech may extend it while this request is blocked in I/O.
        // Fixed network timeouts remain independent; expiry/explicit stop still disconnects promptly.
        val deadline = timeoutExecutor.scheduleWithFixedDelay({
            if (SystemClock.elapsedRealtime() >= requestLimit || scanExpired()) conn.disconnect()
        }, 0, 50, TimeUnit.MILLISECONDS)
        var completed = false
        try {
            conn.connectTimeout = 3_000
            conn.readTimeout = 10_000
            conn.instanceFollowRedirects = false
            conn.setRequestProperty("Accept", "application/json")
            if (jpeg != null) {
                conn.requestMethod = "POST"
                conn.doOutput = true
                conn.setRequestProperty("Content-Type", "image/jpeg")
                conn.setFixedLengthStreamingMode(jpeg.size)
                conn.outputStream.use { it.write(jpeg) }
            }
            if (conn.responseCode !in 200..299) throw IOException("HTTP ${conn.responseCode}")
            val body = conn.inputStream.use { input ->
                val bytes = input.readBytesLimited(64 * 1024)
                bytes.toString(Charsets.UTF_8)
            }
            return JSONObject(body).also { completed = true }
        } catch (error: Exception) {
            if (scanExpired())
                throw CancellationException("Detection window ended").apply { initCause(error) }
            throw error
        } finally {
            deadline.cancel(false)
            // Fully consumed, closed streams can return sockets to Android's HTTP pool.
            // Avoid disconnecting successful requests so idle health checks keep it warm.
            if (!completed) conn.disconnect()
            synchronized(lock) { if (connection === conn) { connection = null; connectionScanId = null } }
        }
    }

    /** Stop only the old scan's upload; the health-check client remains enabled. */
    fun setDetectionScan(scanId: Long?, deadlineAt: Long? = null) {
        val oldRequest = synchronized(lock) {
            activeScanId = scanId
            activeScanDeadlineAt = deadlineAt
            if (connectionScanId != null && connectionScanId != scanId) connection else null
        }
        oldRequest?.disconnect()
    }

    /** Extend only the current, still-live scan; stale audio must not revive an expired request. */
    fun extendDetectionDeadline(scanId: Long, deadlineAt: Long) {
        synchronized(lock) {
            if (activeScanId == scanId && (activeScanDeadlineAt?.let { SystemClock.elapsedRealtime() < it } != false))
                activeScanDeadlineAt = maxOf(activeScanDeadlineAt ?: deadlineAt, deadlineAt)
        }
    }

    private fun java.io.InputStream.readBytesLimited(limit: Int): ByteArray {
        val output = java.io.ByteArrayOutputStream()
        val buffer = ByteArray(4096)
        while (true) {
            val count = read(buffer)
            if (count < 0) break
            if (output.size() + count > limit) throw IOException("Response is too large")
            output.write(buffer, 0, count)
        }
        return output.toByteArray()
    }

    fun resume() { synchronized(lock) { enabled = true } }

    fun cancel() {
        val pending = synchronized(lock) { enabled = false; connection }
        pending?.disconnect()
    }

    fun close() {
        cancel()
        timeoutExecutor.shutdownNow()
    }

    companion object {
        const val MAX_IMAGE_BYTES = 8 * 1024 * 1024
        private const val PROTOCOL_VERSION = 2
    }
}
