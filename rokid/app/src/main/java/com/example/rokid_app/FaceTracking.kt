package com.example.rokid_app

import kotlin.math.max
import kotlin.math.min

/** All geometry is normalized in the upright, unmirrored camera image. */
data class FaceBox(val left: Float, val top: Float, val right: Float, val bottom: Float) {
    val height get() = bottom - top
    val centerX get() = (left + right) / 2
    val centerY get() = (top + bottom) / 2
    fun expanded(factor: Float): FaceBox {
        val halfWidth = (right - left) * factor / 2
        val halfHeight = height * factor / 2
        return FaceBox(centerX - halfWidth, centerY - halfHeight, centerX + halfWidth, centerY + halfHeight)
    }
    fun clipped() = FaceBox(left.coerceIn(0f, 1f), top.coerceIn(0f, 1f), right.coerceIn(0f, 1f), bottom.coerceIn(0f, 1f))
    fun rotatedClockwise(degrees: Int): FaceBox = when ((degrees % 360 + 360) % 360) {
        0 -> this
        90 -> FaceBox(1 - bottom, left, 1 - top, right)
        180 -> FaceBox(1 - right, 1 - bottom, 1 - left, 1 - top)
        270 -> FaceBox(top, 1 - right, bottom, 1 - left)
        else -> error("Expected a quarter-turn rotation")
    }
    fun within(region: FaceBox) = FaceBox(
        region.left + left * (region.right - region.left), region.top + top * region.height,
        region.left + right * (region.right - region.left), region.top + bottom * region.height
    )
    fun overlap(other: FaceBox): Float {
        val intersection = max(0f, min(right, other.right) - max(left, other.left)) *
            max(0f, min(bottom, other.bottom) - max(top, other.top))
        val union = (right - left) * height + (other.right - other.left) * other.height - intersection
        return if (union > 0) intersection / union else 0f
    }
}

data class TrackedFace(val id: Int, val generation: Long, val box: FaceBox)
data class NamedFace(val name: String, val box: FaceBox)
data class FaceLabel(val text: String, val box: FaceBox)

/** Main-thread state. Never transfer a name to a newly acquired/reused tracking ID. */
class FaceTracking {
    private var generation = 0L
    private var tracks = emptyList<TrackedFace>()
    private data class Identity(val name: String, val expiresAt: Long)
    private val identities = mutableMapOf<Long, Identity>()

    fun update(detections: List<Pair<Int, FaceBox>>, allowedIds: Set<Int>? = null): List<TrackedFace> {
        val previous = tracks.associateBy { it.id }
        tracks = detections.distinctBy { it.first }.filter { allowedIds == null || it.first in allowedIds }.map { (id, box) ->
            val old = previous[id]
            val crowded = detections.any { (otherId, otherBox) -> otherId != id && box.overlap(otherBox) > 0.15f }
            // Large jumps break continuity even when the detector keeps the ID.
            TrackedFace(id, if (!crowded && old != null && old.box.overlap(box) > 0.1f) old.generation else ++generation, box)
        }
        identities.keys.retainAll(tracks.map { it.generation }.toSet())
        return tracks.toList()
    }

    fun recognize(snapshot: List<TrackedFace>, faces: List<NamedFace>, submittedAt: Long, now: Long) {
        if (now - submittedAt > 2_000) return
        // Ambiguous overlap is deliberately rejected instead of choosing by list order.
        val candidates = faces.map { face -> snapshot.filter { it.box.overlap(face.box) >= 0.35f } }
        snapshot.forEach { track ->
            if (tracks.none { it.generation == track.generation }) return@forEach
            identities.remove(track.generation)
            val matches = faces.indices.filter { track in candidates[it] }
            if (matches.size == 1 && candidates[matches.single()].size == 1) {
                val face = faces[matches.single()]
                identities[track.generation] = Identity(face.name, submittedAt + 4_000)
            }
        }
    }

    fun labels(now: Long, debug: Boolean): List<FaceLabel> = tracks.mapNotNull { track ->
        val identity = identities[track.generation]?.takeIf { now < it.expiresAt }
        val name = identity?.name ?: if (debug) "Face" else return@mapNotNull null
        FaceLabel(name, track.box)
    }

    fun clear() { tracks = emptyList(); identities.clear() }
    fun clearNames() { identities.clear() }
}

/** Head direction proxy, not eye tracking. Choose one guest in the central 30% of the mapped view. */
fun focusedFace(detections: List<Pair<Int, FaceBox>>, calibration: LabelCalibration): Pair<Int, FaceBox>? =
    detections.filter { (_, box) ->
        val mapped = calibration.map(box)
        mapped.centerX in 0.35f..0.65f && mapped.centerY in 0.35f..0.65f
    }.minByOrNull { (_, box) ->
        val mapped = calibration.map(box)
        (mapped.centerX - 0.5f) * (mapped.centerX - 0.5f) + (mapped.centerY - 0.5f) * (mapped.centerY - 0.5f)
    }

/** First-order optical calibration, valid only around the tested distance and wearer fit. */
data class LabelCalibration(
    val scaleX: Float = 1f, val scaleY: Float = 1f,
    val offsetX: Float = 0f, val offsetY: Float = 0f
) {
    fun map(box: FaceBox) = FaceBox(
        (box.left - 0.5f) * scaleX + 0.5f + offsetX,
        (box.top - 0.5f) * scaleY + 0.5f + offsetY,
        (box.right - 0.5f) * scaleX + 0.5f + offsetX,
        (box.bottom - 0.5f) * scaleY + 0.5f + offsetY
    )
}
