package com.example.rokid_app

import android.Manifest
import android.content.Intent
import android.media.AudioRecord
import android.util.Log
import androidx.test.platform.app.InstrumentationRegistry
import com.konovalov.vad.webrtc.VadWebRTC
import com.konovalov.vad.webrtc.config.FrameSize
import com.konovalov.vad.webrtc.config.Mode
import com.konovalov.vad.webrtc.config.SampleRate
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test
import kotlin.math.abs
import kotlin.math.sqrt

/** Opt-in live-input probe; emits aggregate metadata only, never PCM. */
class AudioInputProbeTest {
    @Test fun foregroundMicrophoneDeliversUsableSamples() {
        val args = InstrumentationRegistry.getArguments()
        assumeTrue(args.getString("audio_probe") == "true")
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val context = instrumentation.targetContext
        for (permission in arrayOf(Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO))
            instrumentation.uiAutomation.grantRuntimePermission(context.packageName, permission)
        val activity = instrumentation.startActivitySync(Intent(context, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        instrumentation.waitForIdleSync()
        try {
            val recorder = SpeechActivityMonitor.createRecorder()
            try {
                recorder.startRecording()
                var silencedFrames=0; var speechFrames=0; var nonzero=0; var peak=0; var sumSquares=0.0
                val frame=ShortArray(320)
                val frameCount=(args.getString("frames") ?: "150").toInt().also { require(it in 150..1500) }
                VadWebRTC(SampleRate.SAMPLE_RATE_16K,FrameSize.FRAME_SIZE_320,Mode.VERY_AGGRESSIVE,50,0).use { vad ->
                    repeat(frameCount) {
                        var offset=0
                        while (offset < frame.size) {
                            val count=recorder.read(frame,offset,frame.size-offset,AudioRecord.READ_BLOCKING)
                            check(count > 0) { "Audio read failed: $count" }; offset+=count
                        }
                        if (recorder.activeRecordingConfiguration?.isClientSilenced == true) silencedFrames++
                        for (sample in frame) {
                            val value=sample.toInt(); if (value != 0) nonzero++
                            peak=maxOf(peak,abs(value)); sumSquares+=value.toDouble()*value
                        }
                        if (vad.isSpeech(frame)) speechFrames++
                    }
                }
                Log.i("FaceAudioProbe", "source=${recorder.audioSource} reported_silenced_frames=$silencedFrames nonzero_samples=$nonzero rms=${sqrt(sumSquares/(frameCount*320))} peak=$peak speech_frames=$speechFrames route_type=${recorder.routedDevice?.type}")
                frame.fill(0)
                // RV101 reports silenced=true even when MIC supplies data; validate the actual signal.
                assertTrue("Microphone returned only zero samples",nonzero > 0)
                if (args.getString("expect_speech") == "true") assertTrue("No live speech detected",speechFrames > 20)
            } finally { runCatching { recorder.stop() }; recorder.release() }
        } finally { instrumentation.runOnMainSync { activity.finish() } }
    }
}
