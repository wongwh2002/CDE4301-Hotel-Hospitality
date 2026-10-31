package com.example.rokid_app

import org.junit.Assert.*
import org.junit.Test

class FaceFocusTest {
    private val center = FaceBox(0.45f, 0.43f, 0.55f, 0.57f)

    @Test fun selectsOnlyTheClosestCenteredGuest() {
        val near = FaceBox(0.5f, 0.43f, 0.6f, 0.57f)
        assertEquals(1, focusedFace(listOf(2 to near, 1 to center), LabelCalibration(2f, 2f))?.first)
    }

    @Test fun rejectsFacesOutsideCalibratedCenter() {
        val offCenter = FaceBox(0.6f, 0.43f, 0.7f, 0.57f)
        assertNotNull(focusedFace(listOf(1 to offCenter), LabelCalibration()))
        assertNull(focusedFace(listOf(1 to offCenter), LabelCalibration(2f, 2f)))
        assertNull(focusedFace(listOf(1 to center.copy(top = 0.7f, bottom = 0.8f)), LabelCalibration()))
    }

    @Test fun leavingFocusInvalidatesAnInFlightIdentity() {
        val tracking = FaceTracking()
        val snapshot = tracking.update(listOf(1 to center), setOf(1))
        tracking.update(listOf(1 to center), emptySet())
        assertTrue(tracking.labels(100, true).isEmpty())
        tracking.update(listOf(1 to center), setOf(1))
        tracking.recognize(snapshot, listOf(NamedFace("Alice", center)), 100, 200)
        assertTrue(tracking.labels(300, false).isEmpty())
    }

    @Test fun visualPaddingKeepsTheFaceCenterFixed() {
        val bigger = center.expanded(1.12f)
        assertEquals(center.centerX, bigger.centerX, 0.00001f)
        assertEquals(center.centerY, bigger.centerY, 0.00001f)
        assertEquals(center.height * 1.12f, bigger.height, 0.00001f)
    }

    @Test fun cropCoordinatesRotateAndRoundTripForEveryCameraRotation() {
        val raw = FaceBox(0.1f, 0.2f, 0.4f, 0.6f)
        val expected = listOf(raw, FaceBox(0.4f, 0.1f, 0.8f, 0.4f),
            FaceBox(0.6f, 0.4f, 0.9f, 0.8f), FaceBox(0.2f, 0.6f, 0.6f, 0.9f))
        listOf(0, 90, 180, 270).forEachIndexed { index, rotation ->
            val upright = raw.rotatedClockwise(rotation)
            assertBox(expected[index], upright)
            assertBox(raw, upright.rotatedClockwise(-rotation))
        }
    }

    @Test fun croppedResponseMapsBackToTheOriginalFrame() {
        val region = FaceBox(0.3f, 0.2f, 0.7f, 0.8f)
        val cropped = FaceBox(0.25f, 0.25f, 0.75f, 0.75f)
        assertBox(FaceBox(0.4f, 0.35f, 0.6f, 0.65f), cropped.within(region))
    }

    private fun assertBox(expected: FaceBox, actual: FaceBox) {
        assertEquals(expected.left, actual.left, 0.00001f)
        assertEquals(expected.top, actual.top, 0.00001f)
        assertEquals(expected.right, actual.right, 0.00001f)
        assertEquals(expected.bottom, actual.bottom, 0.00001f)
    }
}
