package com.example.rokid_app

import java.nio.ByteBuffer

/** Copy just a crop, with bulk row reads rather than one ByteBuffer access per pixel. */
fun copyYuvPlane(
    source: ByteBuffer, rowStride: Int, pixelStride: Int,
    left: Int, top: Int, width: Int, height: Int,
    destination: ByteArray, offset: Int, destinationRowStride: Int, destinationPixelStride: Int
) {
    val buffer = source.duplicate()
    val start = buffer.position()
    val rowBytes = (width - 1) * pixelStride + 1
    val scratch = if (pixelStride == 1 && destinationPixelStride == 1) null else ByteArray(rowBytes)
    for (row in 0 until height) {
        buffer.position(start + (top + row) * rowStride + left * pixelStride)
        val target = offset + row * destinationRowStride
        if (scratch == null) buffer.get(destination, target, width)
        else {
            buffer.get(scratch, 0, rowBytes)
            for (column in 0 until width) {
                destination[target + column * destinationPixelStride] = scratch[column * pixelStride]
            }
        }
    }
}
