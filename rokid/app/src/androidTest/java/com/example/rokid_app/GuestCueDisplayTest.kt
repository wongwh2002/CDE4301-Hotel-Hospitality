package com.example.rokid_app

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.os.SystemClock
import android.view.View
import androidx.test.platform.app.InstrumentationRegistry
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.net.ServerSocket
import kotlin.concurrent.thread

class GuestCueDisplayTest {
    private val cues = listOf(GuestCue("twin_room", "prefer"), GuestCue("shellfish", "allergy"))

    private fun render(name: String, icons: List<GuestCue>): Bitmap {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        lateinit var bitmap: Bitmap
        instrumentation.runOnMainSync {
            val view = FaceOverlayView(instrumentation.targetContext)
            view.measure(View.MeasureSpec.makeMeasureSpec(640, View.MeasureSpec.EXACTLY),
                View.MeasureSpec.makeMeasureSpec(480, View.MeasureSpec.EXACTLY))
            view.layout(0, 0, 640, 480)
            val box = FaceBox(0.10f, 0.22f, 0.35f, 0.70f)
            view.show(listOf(FaceLabel(name, box, icons)), listOf(box))
            bitmap = Bitmap.createBitmap(640, 480, Bitmap.Config.ARGB_8888)
            val canvas = Canvas(bitmap)
            canvas.drawColor(Color.BLACK)
            view.draw(canvas)
            view.clear()
        }
        return bitmap
    }

    private fun lastInkRow(bitmap: Bitmap): Int {
        for (y in bitmap.height - 1 downTo 0) for (x in 0 until bitmap.width) {
            if (Color.green(bitmap.getPixel(x, y)) > 80) return y
        }
        return -1
    }

    @Test fun iconsRenderBelowNameAndUnknownNeverShowsIcons() {
        val withIcons = render("Demo guest", cues)
        val nameOnly = render("Demo guest", emptyList())
        assertTrue("Expected name pixels", lastInkRow(nameOnly) >= 0)
        assertTrue("Icons must appear below the name", lastInkRow(withIcons) > lastInkRow(nameOnly) + 20)
        assertTrue(render("Unknown", cues).sameAs(render("Unknown", emptyList())))
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        File(context.getExternalFilesDir(null), "glasses-cue-overlay-test.png").outputStream().use {
            assertTrue(withIcons.compress(Bitmap.CompressFormat.PNG, 100, it))
        }
    }

    private fun fetch(name: String): List<GuestCue> {
        ServerSocket(0).use { server ->
            server.soTimeout = 5000
            val worker = thread {
                server.accept().use { socket ->
                    socket.soTimeout = 5000
                    val reader = socket.getInputStream().bufferedReader()
                    while (true) { if (reader.readLine().isNullOrEmpty()) break }
                    val face = JSONObject().put("name", name)
                        .put("box", JSONObject().put("x", 10).put("y", 10).put("width", 40).put("height", 40))
                        .put("cues", JSONArray(cues.map { JSONObject().put("code", it.code).put("sentiment", it.sentiment) }))
                    val response = JSONObject().put("request_id", "cue-test").put("protocol_version", 2)
                        .put("image_width", 100).put("image_height", 100).put("display", name)
                        .put("faces", JSONArray().put(face)).toString().toByteArray()
                    socket.getOutputStream().apply {
                        write("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: ${response.size}\r\nConnection: close\r\n\r\n".toByteArray())
                        write(response); flush()
                    }
                }
            }
            val client = FaceServerClient("http://127.0.0.1:${server.localPort}")
            try {
                val deadline = SystemClock.elapsedRealtime() + 5000
                client.setDetectionScan(1, deadline)
                return client.detect(byteArrayOf(1), 0, "cue-test", 1, deadline).faces.single().cues
            } finally { client.close(); worker.join(6000) }
        }
    }

    @Test fun androidHttpClientReadsCuesButDiscardsThemForUnknown() {
        assertEquals(cues, fetch("Demo guest"))
        assertTrue(fetch("Unknown").isEmpty())
    }
}
