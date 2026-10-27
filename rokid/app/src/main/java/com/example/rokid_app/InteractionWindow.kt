package com.example.rokid_app

/** Immutable deadlines shared by the camera executor and UI thread. */
data class InteractionWindow(
    val scanId: Long = 0,
    val detectionUntil: Long = 0,
    val statusUntil: Long = 0
) {
    fun tap(now: Long) = copy(scanId = scanId + 1, detectionUntil = now + DETECTION_MS)
    fun swipeForward(now: Long) = copy(statusUntil = now + STATUS_MS)
    fun stopDetection() = copy(scanId = scanId + 1, detectionUntil = 0)
    fun detecting(now: Long) = now < detectionUntil
    fun showingStatus(now: Long) = now < statusUntil
    fun acceptsResult(id: Long, now: Long) = id == scanId && detecting(now)
    fun canStartRecognition(now: Long) = detecting(now) && detectionUntil - now >= 350

    companion object {
        const val DETECTION_MS = 10_000L
        const val STATUS_MS = 5_000L
    }
}
