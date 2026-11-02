package com.example.rokid_app

import android.annotation.SuppressLint
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.SystemClock
import android.util.Log
import com.konovalov.vad.webrtc.VadWebRTC
import com.konovalov.vad.webrtc.config.FrameSize
import com.konovalov.vad.webrtc.config.Mode
import com.konovalov.vad.webrtc.config.SampleRate
import java.io.IOException
import java.util.concurrent.Executors

/** Tap-scoped microphone/VAD worker. PCM is transient; the authorized capture callback may buffer it for upload. */
class SpeechActivityMonitor : AutoCloseable {
    private class Session {
        @Volatile var stopped = false
        var recorder: AudioRecord? = null // Guarded by lock; only the worker releases it.
    }
    private val lock = Any()
    private val worker = Executors.newSingleThreadExecutor()
    private var current: Session? = null
    private var closed = false

    fun start(onSpeech: (Long) -> Unit, onFailure: (Exception) -> Unit, onReady: () -> Unit = {},
              onAudioFrame: (ShortArray, Boolean, Long) -> Unit = { _, _, _ -> }) {
        stop()
        val session = synchronized(lock) {
            check(!closed) { "Speech monitor closed" }
            Session().also { current = it }
        }
        worker.execute { capture(session, onSpeech, onFailure, onReady, onAudioFrame) }
    }

    @SuppressLint("MissingPermission") // Activity requires RECORD_AUDIO before starting this worker.
    private fun capture(session: Session, onSpeech: (Long) -> Unit, onFailure: (Exception) -> Unit, onReady: () -> Unit,
                        onAudioFrame: (ShortArray, Boolean, Long) -> Unit) {
        if (session.stopped) return
        val frame = ShortArray(320) // 20 ms of mono PCM at 16 kHz.
        try {
            VadWebRTC(SampleRate.SAMPLE_RATE_16K, FrameSize.FRAME_SIZE_320,
                Mode.VERY_AGGRESSIVE, speechDurationMs = 50, silenceDurationMs = 0).use { vad ->
                val recorder = createRecorder()
                try {
                    synchronized(lock) {
                        if (session.stopped || current !== session) return
                        check(recorder.state == AudioRecord.STATE_INITIALIZED) { "Microphone initialization failed" }
                        session.recorder = recorder
                        recorder.startRecording()
                        check(recorder.recordingState == AudioRecord.RECORDSTATE_RECORDING) { "Microphone did not start" }
                    }
                    Log.i("FaceAudio", "microphone_started sample_rate=16000 frame_ms=20")
                    onReady()
                    var offset = 0
                    var lastSpeechCallback = Long.MIN_VALUE / 2
                    while (!session.stopped) {
                        val count = recorder.read(frame, offset, frame.size - offset, AudioRecord.READ_BLOCKING)
                        if (session.stopped) break
                        if (count <= 0) throw IOException("Microphone read failed: $count")
                        offset += count
                        if (offset == frame.size) {
                            val at = SystemClock.elapsedRealtime()
                            val detectedSpeech = vad.isSpeech(frame)
                            onAudioFrame(frame, detectedSpeech, at) // Callback must consume/copy synchronously.
                            if (detectedSpeech && at - lastSpeechCallback >= 200) {
                                lastSpeechCallback = at
                                onSpeech(at)
                            }
                            offset = 0
                        }
                    }
                } finally {
                    synchronized(lock) {
                        session.recorder = null
                        recorder.release()
                    }
                }
            }
        } catch (error: Exception) {
            if (!session.stopped) onFailure(error)
        } catch (error: LinkageError) {
            if (!session.stopped) onFailure(IllegalStateException("Speech detector unavailable on this device", error))
        } finally {
            frame.fill(0)
            synchronized(lock) { if (current === session) current = null }
            Log.i("FaceAudio", "microphone_stopped")
        }
    }

    /** Stop unblocks a pending read; its worker owns final recorder/VAD release. */
    fun stop() {
        synchronized(lock) {
            val session = current ?: return
            session.stopped = true
            current = null
            runCatching { session.recorder?.stop() }
        }
    }

    override fun close() {
        synchronized(lock) { closed = true }
        stop()
        worker.shutdown()
    }

    companion object {
        @SuppressLint("MissingPermission")
        internal fun createRecorder(): AudioRecord {
            val minimum = AudioRecord.getMinBufferSize(16_000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT)
            check(minimum > 0) { "16 kHz microphone input unavailable" }
            // RV101 firmware initializes VOICE_RECOGNITION successfully but returns only zeros.
            // MIC supplies actual samples; keep the production input shared with the device regression probe.
            return AudioRecord.Builder().setAudioSource(MediaRecorder.AudioSource.MIC)
                .setAudioFormat(AudioFormat.Builder().setSampleRate(16_000)
                    .setChannelMask(AudioFormat.CHANNEL_IN_MONO).setEncoding(AudioFormat.ENCODING_PCM_16BIT).build())
                .setBufferSizeInBytes(maxOf(minimum * 2, 5120)).build()
        }
    }
}
