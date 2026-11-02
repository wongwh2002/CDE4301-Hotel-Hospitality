package com.example.rokid_app

import android.os.SystemClock
import org.junit.Assert.*
import org.junit.Test
import java.io.DataInputStream
import java.net.ServerSocket
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicReference

class PreferenceUploadTest {
    @Test fun uploadsWavWithBindingAndValidatesCorrelatedResponse() {
        val buffer=ConversationAudioBuffer("transport-test")
        buffer.observeIdentity(PreferenceGuest("Test Guest","test-binding"),1,1000)
        buffer.observeIdentity(PreferenceGuest("Test Guest","test-binding"),1,1100)
        buffer.updateVisibility(RecognizedGuest("Test Guest",1),1100)
        repeat(30) { buffer.append(ShortArray(320) { 1234 },true,1200) }
        val audio=buffer.finish()!!
        ServerSocket(0).use { server ->
            val executor=Executors.newSingleThreadExecutor()
            val failure=AtomicReference<Throwable?>()
            val received=AtomicReference<ByteArray>()
            val task=executor.submit {
                try {
                    server.accept().use { socket ->
                        socket.soTimeout=5000
                        val input=DataInputStream(socket.getInputStream())
                        val headers=StringBuilder()
                        while (!headers.endsWith("\r\n\r\n")) { headers.append(input.readUnsignedByte().toChar()); check(headers.length < 8192) }
                        val text=headers.toString()
                        check(text.startsWith("POST /audio/preferences?request_id=transport-test "))
                        check(text.contains("X-Guest-Token: test-binding",ignoreCase=true))
                        check(text.contains("Content-Type: audio/wav",ignoreCase=true))
                        val length=Regex("Content-Length: (\\d+)",RegexOption.IGNORE_CASE).find(text)!!.groupValues[1].toInt()
                        received.set(ByteArray(length).also { input.readFully(it) })
                        val body="""{"capture_id":"transport-test","status":"completed","saved_count":1}"""
                        socket.getOutputStream().write(("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: ${body.length}\r\nConnection: close\r\n\r\n"+body).toByteArray())
                    }
                } catch(error:Throwable) { failure.set(error) }
            }
            try {
                PreferenceClient("http://127.0.0.1:${server.localPort}").use { client ->
                    val result=client.upload(audio)
                    assertEquals(1,result.getInt("saved_count")); assertArrayEquals(audio.wav,received.get())
                }
                task.get(); assertNull(failure.get())
            } finally { executor.shutdownNow() }
        }
    }
}
