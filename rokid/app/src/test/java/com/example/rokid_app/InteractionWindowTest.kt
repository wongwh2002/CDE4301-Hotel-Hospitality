package com.example.rokid_app

import org.junit.Assert.*
import org.junit.Test

class InteractionWindowTest {
    @Test fun startsBlackAndIdle() {
        val window = InteractionWindow()
        assertFalse(window.detecting(0))
        assertFalse(window.showingStatus(0))
    }

    @Test fun tapPermitsResultsForExactlyFifteenSecondsOfSilence() {
        val window = InteractionWindow().tap(1_000)
        assertTrue(window.acceptsResult(window.scanId, 15_999))
        assertFalse(window.acceptsResult(window.scanId, 16_000))
        assertFalse(window.showingStatus(1_000))
    }

    @Test fun refusesNewUploadsNearTheEndOfTheWindow() {
        val window = InteractionWindow().tap(1_000)
        assertTrue(window.canStartRecognition(15_650))
        assertFalse(window.canStartRecognition(15_651))
        assertFalse(window.canStartRecognition(16_000))
    }

    @Test fun anotherTapRestartsCountdownAndRejectsOldResults() {
        val first = InteractionWindow().tap(1_000)
        val second = first.tap(9_000)
        assertFalse(second.acceptsResult(first.scanId, 9_100))
        assertTrue(second.acceptsResult(second.scanId, 23_999))
        assertFalse(second.detecting(24_000))
    }

    @Test fun swipeOnlyShowsStatusAndDoesNotStartDetection() {
        val window = InteractionWindow().swipeForward(1_000)
        assertFalse(window.detecting(1_000))
        assertTrue(window.showingStatus(5_999))
        assertFalse(window.showingStatus(6_000))
    }

    @Test fun statusPeekDoesNotExtendTheDetectionDeadline() {
        val window = InteractionWindow().tap(1_000).swipeForward(15_000)
        assertFalse(window.detecting(16_000))
        assertTrue(window.showingStatus(16_000))
    }

    @Test fun stopRejectsInFlightResultsAndPreservesIndependentStatusPeek() {
        val running = InteractionWindow().tap(1_000).swipeForward(2_000)
        val stopped = running.stopDetection()
        assertFalse(stopped.acceptsResult(running.scanId, 3_000))
        assertFalse(stopped.detecting(3_000))
        assertTrue(stopped.showingStatus(3_000))
    }

    @Test fun speechExtendsTheExistingScanWithoutInvalidatingPendingIdentities() {
        val first = InteractionWindow().tap(1_000)
        val extended = first.speech(first.scanId, 14_000)
        assertEquals(first.scanId, extended.scanId)
        assertEquals(1_000L, extended.detectionStartedAt)
        assertTrue(extended.acceptsResult(first.scanId, 28_999))
        assertFalse(extended.detecting(29_000))
    }

    @Test fun speechCannotStartIdleOrReviveExpiredDetection() {
        val idle = InteractionWindow()
        assertEquals(idle, idle.speech(idle.scanId, 1_000))
        val running = idle.tap(1_000)
        assertEquals(running, running.speech(running.scanId, 16_000))
        assertEquals(running, running.speech(running.scanId, 17_000))
    }

    @Test fun staleAudioDoesNotExtendANewScanOrMoveDeadlineBackwards() {
        val first = InteractionWindow().tap(1_000)
        val second = first.tap(4_000)
        assertEquals(second, second.speech(first.scanId, 5_000))
        assertEquals(second, second.speech(second.scanId, 3_999))
        val extended = second.speech(second.scanId, 9_000)
        assertEquals(extended, extended.speech(second.scanId, 8_000))
    }

    @Test fun ongoingConversationCanOutlastOneMinuteThenTimesOutAfterLastSpeech() {
        var window = InteractionWindow().tap(1_000)
        for (at in 1_000L..61_000L step 1_000L) window = window.speech(window.scanId, at)
        assertTrue(window.detecting(75_999))
        assertFalse(window.detecting(76_000))
        assertFalse(window.stopDetection().speech(window.scanId, 70_000).detecting(70_000))
    }
}
