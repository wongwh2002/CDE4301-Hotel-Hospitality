package com.example.rokid_app

import android.os.SystemClock
import android.util.Log
import androidx.test.platform.app.InstrumentationRegistry
import com.konovalov.vad.webrtc.VadWebRTC
import com.konovalov.vad.webrtc.config.FrameSize
import com.konovalov.vad.webrtc.config.Mode
import com.konovalov.vad.webrtc.config.SampleRate
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.UUID

/** Opt-in synthetic replay from the glasses to real server models and an isolated test database. */
class PreferencePipelineDeviceTest {
    @Test fun syntheticConversationReachesServerAndPersistsPreferences() {
        val args=InstrumentationRegistry.getArguments()
        assumeTrue("Opt in with -e preference_e2e true",args.getString("preference_e2e")=="true")
        val instrumentation=InstrumentationRegistry.getInstrumentation()
        val server=args.getString("server") ?: error("Pass isolated test server URL")
        val photo=File(instrumentation.targetContext.filesDir,"preference-fixture.jpg").readBytes()
        val bytes=instrumentation.context.assets.open("synthetic-preference-16k-mono.pcm").use { it.readBytes() }
        val pcm=ShortArray(bytes.size/2)
        ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer().get(pcm)
        val captureId=UUID.randomUUID().toString()
        val capture=ConversationAudioBuffer(captureId)
        val faceClient=FaceServerClient(server)
        try {
            faceClient.checkHealth()
            val deadline=SystemClock.elapsedRealtime()+180000
            faceClient.setDetectionScan(1,deadline)
            var binding:PreferenceGuest?=null
            fun identify() {
                val response=faceClient.detect(photo,0,UUID.randomUUID().toString(),1,deadline)
                val next=response.preferenceGuest ?: error("Reference was not recognized as one guest")
                if (binding!=null) assertEquals(binding!!.name,next.name)
                binding=next
                capture.observeIdentity(next,1,SystemClock.elapsedRealtime())
            }
            identify(); identify()
            VadWebRTC(SampleRate.SAMPLE_RATE_16K,FrameSize.FRAME_SIZE_320,Mode.VERY_AGGRESSIVE,50,0).use { vad ->
                for (offset in 0..pcm.size-320 step 320) {
                    if (offset>0 && offset%32000==0) identify()
                    val at=SystemClock.elapsedRealtime()
                    capture.updateVisibility(RecognizedGuest(binding!!.name,1),at)
                    val frame=pcm.copyOfRange(offset,offset+320)
                    capture.append(frame,vad.isSpeech(frame),at)
                    SystemClock.sleep(20)
                }
            }
            faceClient.setDetectionScan(null) // Final audio processing must survive detection ending.
            val audio=capture.finish() ?: error("No authorized speech was buffered")
            PreferenceClient(server).use { client ->
                val result=client.upload(audio)
                assertEquals(captureId,result.getString("capture_id"))
                assertTrue("Expected coffee and room preferences",result.getInt("saved_count")>=2)
                assertEquals(result.getString("guest_id"),client.upload(audio).getString("guest_id"))
                Log.i("PreferencePipelineTest","PASS capture_id=$captureId saved_count=${result.getInt("saved_count")}")
            }
            faceClient.checkHealth()
        } finally { faceClient.close() }
    }
}
