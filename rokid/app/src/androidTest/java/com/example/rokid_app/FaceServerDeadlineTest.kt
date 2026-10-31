package com.example.rokid_app

import android.os.SystemClock
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.net.ServerSocket
import java.net.Socket
import java.util.concurrent.CancellationException
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.CountDownLatch
import java.util.concurrent.ExecutionException
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

/** Real Android HTTP connections against a deliberately stalled local recognition endpoint. */
@RunWith(AndroidJUnit4::class)
class FaceServerDeadlineTest {
    @Test fun scanDeadlineInterruptsAStalledResponseWithoutDisablingHealthChecks() {
        verifyCancellation(explicitStop = false)
    }

    @Test fun stoppingScanInterruptsUploadWithoutDisablingHealthChecks() {
        verifyCancellation(explicitStop = true)
    }

    private fun verifyCancellation(explicitStop: Boolean) {
        DelayedServer().use { server ->
            val client = FaceServerClient("http://127.0.0.1:${server.port}")
            val executor = Executors.newSingleThreadExecutor()
            try {
                client.setDetectionScan(1)
                val started = SystemClock.elapsedRealtime()
                val deadline = started + if (explicitStop) 10_000 else 1_000
                val result = executor.submit<FaceServerResult> {
                    client.detect(byteArrayOf(1, 2, 3), 0, "deadline-test", 1, deadline)
                }
                assertTrue("Recognition request never reached test server", server.detectReceived.await(2, TimeUnit.SECONDS))
                if (explicitStop) client.setDetectionScan(null)
                try {
                    result.get(3, TimeUnit.SECONDS)
                    fail("Expired recognition should have been cancelled")
                } catch (error: ExecutionException) {
                    assertTrue("Unexpected failure: ${error.cause}", error.cause is CancellationException)
                }
                assertTrue("Cancellation waited too long", SystemClock.elapsedRealtime() - started < 3_000)
                client.checkHealth()
                assertTrue("Health checks did not survive scan cancellation", server.healthReceived.await(1, TimeUnit.SECONDS))
            } finally {
                client.close()
                executor.shutdownNow()
            }
        }
    }

    private class DelayedServer : AutoCloseable {
        private val server = ServerSocket(0)
        val port get() = server.localPort
        val detectReceived = CountDownLatch(1)
        val healthReceived = CountDownLatch(1)
        private val holdDetection = CountDownLatch(1)
        private val sockets = CopyOnWriteArrayList<Socket>()
        private val workers = Executors.newCachedThreadPool()

        init {
            workers.execute {
                while (!server.isClosed) {
                    val socket = try { server.accept() } catch (_: Exception) { break }
                    sockets.add(socket)
                    workers.execute {
                        runCatching {
                            socket.use {
                                it.soTimeout = 3_000
                                val reader = it.getInputStream().bufferedReader(Charsets.ISO_8859_1)
                                val line = reader.readLine() ?: return@use
                                var length = 0
                                while (true) {
                                    val header = reader.readLine() ?: return@use
                                    if (header.isEmpty()) break
                                    if (header.startsWith("Content-Length:", ignoreCase = true))
                                        length = header.substringAfter(':').trim().toInt()
                                }
                                repeat(length) { check(reader.read() != -1) }
                                if (line.startsWith("POST /detect")) {
                                    detectReceived.countDown()
                                    holdDetection.await()
                                } else {
                                    healthReceived.countDown()
                                    val body = "{\"status\":\"ready\",\"protocol_version\":2}"
                                    it.getOutputStream().write(("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n" +
                                        "Content-Length: ${body.length}\r\nConnection: close\r\n\r\n" + body).toByteArray())
                                }
                            }
                        }
                    }
                }
            }
        }

        override fun close() {
            server.close()
            sockets.forEach { runCatching { it.close() } }
            holdDetection.countDown()
            workers.shutdownNow()
        }
    }
}
