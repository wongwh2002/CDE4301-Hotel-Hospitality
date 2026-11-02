package com.example.rokid_app

import android.Manifest
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.konovalov.vad.webrtc.VadWebRTC
import com.konovalov.vad.webrtc.config.FrameSize
import com.konovalov.vad.webrtc.config.Mode
import com.konovalov.vad.webrtc.config.SampleRate
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

@RunWith(AndroidJUnit4::class)
class SpeechActivityMonitorTest {
    private fun vad() = VadWebRTC(SampleRate.SAMPLE_RATE_16K, FrameSize.FRAME_SIZE_320,
        Mode.VERY_AGGRESSIVE, speechDurationMs = 50, silenceDurationMs = 0)

    @Test fun nativeDetectorRejectsSilence() {
        vad().use { detector ->
            repeat(200) { assertFalse(detector.isSpeech(ShortArray(320))) }
        }
    }

    @Test fun nativeDetectorRecognizesSyntheticSpeech() {
        val bytes = InstrumentationRegistry.getInstrumentation().context.assets
            .open("synthetic-speech-16k-mono.pcm").use { it.readBytes() }
        val pcm = ShortArray(bytes.size / 2)
        ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer().get(pcm)
        vad().use { detector ->
            var speechFrames = 0
            for (offset in 0..pcm.size - 320 step 320)
                if (detector.isSpeech(pcm.copyOfRange(offset, offset + 320))) speechFrames++
            assertTrue("Synthetic speech was never recognized", speechFrames > 20)
            // Internal VAD hangover may retain a few frames, but must not retain sustained silence.
            repeat(50) { detector.isSpeech(ShortArray(320)) }
            repeat(100) { assertFalse(detector.isSpeech(ShortArray(320))) }
        }
    }

    @Test fun microphoneCanBeStoppedAndReopened() {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        instrumentation.uiAutomation.grantRuntimePermission(instrumentation.targetContext.packageName, Manifest.permission.RECORD_AUDIO)
        val failure = AtomicReference<Exception?>()
        SpeechActivityMonitor().use { monitor ->
            repeat(2) {
                val ready = CountDownLatch(1)
                monitor.start(onSpeech = {}, onFailure = { error -> failure.set(error); ready.countDown() }, onReady = { ready.countDown() })
                assertTrue("Microphone worker did not start", ready.await(3, TimeUnit.SECONDS))
                assertNull("Microphone failed: ${failure.get()}", failure.get())
                monitor.stop()
            }
        }
    }
}
