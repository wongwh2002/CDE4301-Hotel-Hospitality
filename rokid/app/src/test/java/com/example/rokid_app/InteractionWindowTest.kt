package com.example.rokid_app

import org.junit.Assert.*
import org.junit.Test

class InteractionWindowTest {
    @Test fun startsBlackAndIdle() {
        val window = InteractionWindow()
        assertFalse(window.detecting(0))
        assertFalse(window.showingStatus(0))
    }

    @Test fun tapPermitsResultsForExactlyTenSeconds() {
        val window = InteractionWindow().tap(1_000)
        assertTrue(window.acceptsResult(window.scanId, 10_999))
        assertFalse(window.acceptsResult(window.scanId, 11_000))
        assertFalse(window.showingStatus(1_000))
    }

    @Test fun refusesNewUploadsNearTheEndOfTheWindow() {
        val window = InteractionWindow().tap(1_000)
        assertTrue(window.canStartRecognition(10_650))
        assertFalse(window.canStartRecognition(10_651))
        assertFalse(window.canStartRecognition(11_000))
    }

    @Test fun anotherTapRestartsCountdownAndRejectsOldResults() {
        val first = InteractionWindow().tap(1_000)
        val second = first.tap(9_000)
        assertFalse(second.acceptsResult(first.scanId, 9_100))
        assertTrue(second.acceptsResult(second.scanId, 18_999))
        assertFalse(second.detecting(19_000))
    }

    @Test fun swipeOnlyShowsStatusAndDoesNotStartDetection() {
        val window = InteractionWindow().swipeForward(1_000)
        assertFalse(window.detecting(1_000))
        assertTrue(window.showingStatus(5_999))
        assertFalse(window.showingStatus(6_000))
    }

    @Test fun statusPeekDoesNotExtendTheDetectionDeadline() {
        val window = InteractionWindow().tap(1_000).swipeForward(10_000)
        assertFalse(window.detecting(11_000))
        assertTrue(window.showingStatus(11_000))
    }

    @Test fun stopRejectsInFlightResultsAndPreservesIndependentStatusPeek() {
        val running = InteractionWindow().tap(1_000).swipeForward(2_000)
        val stopped = running.stopDetection()
        assertFalse(stopped.acceptsResult(running.scanId, 3_000))
        assertFalse(stopped.detecting(3_000))
        assertTrue(stopped.showingStatus(3_000))
    }
}
