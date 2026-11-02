package com.example.rokid_app

import android.graphics.ImageFormat
import android.graphics.Rect
import android.graphics.YuvImage
import androidx.camera.core.ImageProxy
import java.io.ByteArrayOutputStream

data class RecognitionFrame(val jpeg: ByteArray, val uprightRegion: FaceBox)

/** Copy YUV planes and encode only the focused guest's padded crop. */
fun cameraJpeg(image: ImageProxy, uprightFace: FaceBox): RecognitionFrame {
    require(image.format == ImageFormat.YUV_420_888)
    val width = image.width
    val height = image.height
    require(width % 2 == 0 && height % 2 == 0)
    val raw = uprightFace.expanded(1.6f).clipped().rotatedClockwise(-image.imageInfo.rotationDegrees)
    // Align outwards to the NV21 chroma grid; use the actual aligned crop for response mapping.
    val crop = Rect(
        (kotlin.math.floor(raw.left * width / 2).toInt() * 2).coerceIn(0, width - 2),
        (kotlin.math.floor(raw.top * height / 2).toInt() * 2).coerceIn(0, height - 2),
        (kotlin.math.ceil(raw.right * width / 2).toInt() * 2).coerceIn(2, width),
        (kotlin.math.ceil(raw.bottom * height / 2).toInt() * 2).coerceIn(2, height)
    )
    require(crop.width() > 0 && crop.height() > 0)
    val region = FaceBox(crop.left.toFloat() / width, crop.top.toFloat() / height,
        crop.right.toFloat() / width, crop.bottom.toFloat() / height).rotatedClockwise(image.imageInfo.rotationDegrees)
    val cropWidth = crop.width()
    val cropHeight = crop.height()
    val pixels = cropWidth * cropHeight
    val nv21 = ByteArray(pixels * 3 / 2)
    image.planes.forEachIndexed { index, plane ->
        val divisor = if (index == 0) 1 else 2
        val offset = when (index) { 0 -> 0; 1 -> pixels + 1; else -> pixels }
        copyYuvPlane(plane.buffer, plane.rowStride, plane.pixelStride,
            crop.left / divisor, crop.top / divisor, cropWidth / divisor, cropHeight / divisor,
            nv21, offset, cropWidth, if (index == 0) 1 else 2)
    }
    return ByteArrayOutputStream().use { output ->
        check(YuvImage(nv21, ImageFormat.NV21, cropWidth, cropHeight, null)
            .compressToJpeg(Rect(0, 0, cropWidth, cropHeight), 80, output))
        RecognitionFrame(output.toByteArray(), region)
    }
}
