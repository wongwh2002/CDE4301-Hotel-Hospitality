package com.example.rokid_app

import org.json.JSONObject
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

data class FaceServerResult(val display: String, val inferenceMs: Double, val faceCount: Int)

/** Small HTTP client; called only on the I/O executor. */
class FaceServerClient(baseUrl: String) {
    private val lock = Any()
    private var enabled = true
    private val base = baseUrl.trimEnd('/')
    private val timeoutExecutor = Executors.newSingleThreadScheduledExecutor()
    @Volatile private var connection: HttpURLConnection? = null

    fun checkHealth() {
        val response = request("/health")
        check(response.optString("status") == "ready" && response.optInt("protocol_version") == PROTOCOL_VERSION) {
            "Incompatible or unready server"
        }
    }

    fun detect(jpeg: ByteArray, rotation: Int, requestId: String): FaceServerResult {
        val response = request("/detect?rotation=$rotation&request_id=$requestId", jpeg)
        check(response.getString("request_id") == requestId) { "Response ID mismatch" }
        check(response.getInt("protocol_version") == PROTOCOL_VERSION) { "Incompatible server" }
        return FaceServerResult(
            response.getString("display").take(500).ifBlank { "Unknown" },
            response.optDouble("inference_ms", Double.NaN),
            response.optJSONArray("faces")?.length() ?: 0
        )
    }

    private fun request(path: String, jpeg: ByteArray? = null): JSONObject {
        val conn = synchronized(lock) {
            check(enabled) { "Client stopped" }
            (URL(base + path).openConnection() as HttpURLConnection).also { connection = it }
        }
        val deadline = timeoutExecutor.schedule({ conn.disconnect() }, 12, TimeUnit.SECONDS)
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
            return JSONObject(body)
        } finally {
            deadline.cancel(false)
            conn.disconnect()
            if (connection === conn) connection = null
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
