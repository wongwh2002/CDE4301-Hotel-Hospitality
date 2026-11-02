package com.example.rokid_app

import android.util.Log
import org.json.JSONObject
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.ArrayBlockingQueue
import java.util.concurrent.RejectedExecutionException
import java.util.concurrent.ThreadPoolExecutor
import java.util.concurrent.TimeUnit
import java.util.concurrent.Executors
import java.util.concurrent.ScheduledFuture

/** Slow audio processing is independent of face requests, scan deadlines and health checks. */
class PreferenceClient(baseUrl: String) : AutoCloseable {
    private val base = baseUrl.trimEnd('/')
    private val worker = ThreadPoolExecutor(1,1,0,TimeUnit.MILLISECONDS,ArrayBlockingQueue(1))
    private val deadlines = Executors.newSingleThreadScheduledExecutor()
    @Volatile private var closed = false
    @Volatile private var pending: HttpURLConnection? = null

    fun submit(audio: PreferenceAudio): Boolean {
        if (closed) return false
        return try {
            worker.execute {
                try {
                    val result = upload(audio)
                    Log.i("PreferenceCapture", "completed capture_id=${audio.captureId} saved_count=${result.getInt("saved_count")}")
                } catch (error: Exception) {
                    // Do not log names, transcripts, provider secrets, or opaque guest-binding tokens.
                    Log.w("PreferenceCapture", "failed capture_id=${audio.captureId} error_type=${error.javaClass.simpleName}")
                }
            }
            true
        } catch (_: RejectedExecutionException) { false }
    }

    internal fun upload(audio: PreferenceAudio): JSONObject {
        check(!closed)
        val connection = URL("$base/audio/preferences?request_id=${audio.captureId}").openConnection() as HttpURLConnection
        pending = connection
        var deadline: ScheduledFuture<*>? = null
        try {
            check(!closed)
            deadline = deadlines.schedule({ connection.disconnect() }, 120, TimeUnit.SECONDS)
            connection.requestMethod = "POST"
            connection.connectTimeout = 3_000
            connection.readTimeout = 120_000
            connection.instanceFollowRedirects = false
            connection.doOutput = true
            connection.setRequestProperty("Content-Type","audio/wav")
            connection.setRequestProperty("Accept","application/json")
            connection.setRequestProperty("X-Guest-Token",audio.guestToken)
            connection.setFixedLengthStreamingMode(audio.wav.size)
            connection.outputStream.use { it.write(audio.wav) }
            if (connection.responseCode !in 200..299) throw IOException("Preference HTTP ${connection.responseCode}")
            val body = connection.inputStream.use { input ->
                val output=java.io.ByteArrayOutputStream(); val buffer=ByteArray(4096)
                while (true) {
                    val count=input.read(buffer); if (count < 0) break
                    if (output.size()+count > 64*1024) throw IOException("Preference response too large")
                    output.write(buffer,0,count)
                }
                output.toString(Charsets.UTF_8.name())
            }
            return JSONObject(body).also { check(it.getString("capture_id") == audio.captureId && it.getString("status") == "completed") }
        } finally { deadline?.cancel(false); connection.disconnect(); if (pending === connection) pending = null }
    }

    override fun close() { closed=true; pending?.disconnect(); worker.shutdownNow(); deadlines.shutdownNow() }
}
