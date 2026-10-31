package com.example.rokid_app

import org.junit.Assert.*
import org.junit.Test

class FaceTrackingTest {
    private val left = FaceBox(0.1f, 0.2f, 0.3f, 0.5f)
    private val right = FaceBox(0.6f, 0.2f, 0.8f, 0.5f)

    @Test fun namesFollowIdsWhenDetectionOrderChanges() {
        val tracking = FaceTracking()
        val snapshot = tracking.update(listOf(1 to left, 2 to right))
        tracking.update(listOf(2 to right, 1 to left.copy(left = 0.11f)))
        tracking.recognize(snapshot, listOf(NamedFace("Alice", left), NamedFace("Bob", right)), 100, 400)
        assertEquals(listOf("Bob", "Alice"), tracking.labels(500, false).map { it.text })
    }

    @Test fun debugLabelDoesNotExposeTemporaryDetectorId() {
        val tracking = FaceTracking()
        tracking.update(listOf(1 to left))
        assertEquals("Face", tracking.labels(100, true).single().text)
        tracking.update(emptyList())
        tracking.update(listOf(87 to left))
        assertEquals("Face", tracking.labels(200, true).single().text)
        assertTrue(tracking.labels(200, false).isEmpty())
    }

    @Test fun lateResponseCannotNameReacquiredFaceWithReusedId() {
        val tracking = FaceTracking()
        val snapshot = tracking.update(listOf(1 to left))
        tracking.update(emptyList())
        tracking.update(listOf(1 to left))
        tracking.recognize(snapshot, listOf(NamedFace("Alice", left)), 100, 400)
        assertTrue(tracking.labels(500, false).isEmpty())
    }

    @Test fun overlappingFacesAreAmbiguousAndNotNamed() {
        val tracking = FaceTracking()
        val snapshot = tracking.update(listOf(1 to left, 2 to left))
        tracking.recognize(snapshot, listOf(NamedFace("Alice", left)), 100, 400)
        assertTrue(tracking.labels(500, false).isEmpty())
    }

    @Test fun expiredResultsAndNamesAreHidden() {
        val tracking = FaceTracking()
        val snapshot = tracking.update(listOf(1 to left))
        tracking.recognize(snapshot, listOf(NamedFace("Alice", left)), 100, 2_101)
        assertTrue(tracking.labels(2_102, false).isEmpty())
        tracking.recognize(snapshot, listOf(NamedFace("Alice", left)), 100, 400)
        assertEquals("Alice", tracking.labels(500, false).single().text)
        assertTrue(tracking.labels(4_100, false).isEmpty())
    }

    @Test fun failedAssociationClearsPreviousName() {
        val tracking = FaceTracking()
        val snapshot = tracking.update(listOf(1 to left))
        tracking.recognize(snapshot, listOf(NamedFace("Alice", left)), 100, 400)
        tracking.recognize(snapshot, emptyList(), 500, 700)
        assertTrue(tracking.labels(800, false).isEmpty())
    }

    @Test fun largeJumpBreaksContinuity() {
        val tracking = FaceTracking()
        val snapshot = tracking.update(listOf(1 to left))
        tracking.update(listOf(1 to right))
        tracking.recognize(snapshot, listOf(NamedFace("Alice", left)), 100, 400)
        assertTrue(tracking.labels(500, false).isEmpty())
    }

    @Test fun crossingFacesInvalidateInFlightNames() {
        val tracking = FaceTracking()
        val snapshot = tracking.update(listOf(1 to left, 2 to right))
        tracking.update(listOf(1 to left, 2 to left))
        tracking.recognize(snapshot, listOf(NamedFace("Alice", left), NamedFace("Bob", right)), 100, 400)
        assertTrue(tracking.labels(500, false).isEmpty())
    }

    @Test fun calibrationScalesAroundCenterAndAddsOffset() {
        val result = LabelCalibration(2f, 0.5f, 0.1f, -0.1f).map(FaceBox(0.4f, 0.2f, 0.6f, 0.8f))
        assertEquals(0.4f, result.left, 0.0001f)
        assertEquals(0.8f, result.right, 0.0001f)
        assertEquals(0.25f, result.top, 0.0001f)
        assertEquals(0.55f, result.bottom, 0.0001f)
    }
}
