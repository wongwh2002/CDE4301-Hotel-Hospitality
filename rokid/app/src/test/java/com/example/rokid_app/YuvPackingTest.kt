package com.example.rokid_app

import org.junit.Assert.*
import org.junit.Test
import java.nio.ByteBuffer

class YuvPackingTest {
    @Test fun copiesOnlyTheRequestedLumaCropWithRowPaddingAndBufferOffset() {
        val source = ByteBuffer.wrap(byteArrayOf(99, 0, 1, 2, 3, 88, 4, 5, 6, 7, 88, 8, 9, 10, 11))
        source.position(1)
        val output = ByteArray(4)
        copyYuvPlane(source, 5, 1, 1, 1, 2, 2, output, 0, 2, 1)
        assertArrayEquals(byteArrayOf(5, 6, 9, 10), output)
        assertEquals(1, source.position())
    }

    @Test fun interleavesStridedChromaIntoNv21OrderWithoutReadingPastTheLastPixel() {
        val u = ByteBuffer.wrap(byteArrayOf(99, 10, 88, 11, 88, 88, 12, 88, 13))
        val v = ByteBuffer.wrap(byteArrayOf(99, 20, 88, 21, 88, 88, 22, 88, 23))
        u.position(1); v.position(1)
        val output = ByteArray(8)
        copyYuvPlane(v, 5, 2, 0, 0, 2, 2, output, 0, 4, 2)
        copyYuvPlane(u, 5, 2, 0, 0, 2, 2, output, 1, 4, 2)
        assertArrayEquals(byteArrayOf(20, 10, 21, 11, 22, 12, 23, 13), output)
    }

    @Test fun supportsPlanarChromaAndNonzeroCropOrigin() {
        val source = ByteBuffer.wrap(byteArrayOf(0, 1, 2, 99, 3, 4, 5, 99, 6, 7, 8))
        val output = ByteArray(8) { 42 }
        copyYuvPlane(source, 4, 1, 1, 1, 2, 2, output, 1, 4, 2)
        assertArrayEquals(byteArrayOf(42, 4, 42, 5, 42, 7, 42, 8), output)
    }
}
