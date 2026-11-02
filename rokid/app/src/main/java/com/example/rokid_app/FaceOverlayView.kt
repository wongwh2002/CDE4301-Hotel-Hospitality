package com.example.rokid_app

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.RectF
import android.graphics.drawable.Drawable
import android.os.SystemClock
import android.util.AttributeSet
import android.util.TypedValue
import android.view.View
import androidx.appcompat.content.res.AppCompatResources

class FaceOverlayView(context: Context, attrs: AttributeSet? = null) : View(context, attrs) {
    @Volatile var calibration = LabelCalibration()
        set(value) { field = value; layoutLabels(); invalidate() }
    var debug = false
    private var labels = emptyList<FaceLabel>()
    private var faces = emptyList<FaceBox>()
    private var updatedAt = 0L
    private val textPaint = android.text.TextPaint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.GREEN }
    private val linePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.GREEN; style = Paint.Style.STROKE; strokeWidth = 1.5f
    }
    private data class DrawLabel(val text: String, val bounds: RectF, val size: Float, val baseline: Float,
                                 val cues: List<GuestCue>, val iconSize: Float, val iconTop: Float)
    private val cueDrawables = mutableMapOf<Int, Drawable>()
    private val cueBounds = RectF()
    private val markerBounds = RectF()
    private var faceRects = emptyList<RectF>()
    private var drawLabels = emptyList<DrawLabel>()
    private val expire = Runnable { clear() }

    fun show(labels: List<FaceLabel>, faces: List<FaceBox>) {
        this.labels = labels; this.faces = faces
        updatedAt = SystemClock.elapsedRealtime()
        removeCallbacks(expire)
        postDelayed(expire, 500)
        layoutLabels()
        invalidate()
    }

    fun clear() {
        removeCallbacks(expire); labels = emptyList(); faces = emptyList()
        faceRects = emptyList(); drawLabels = emptyList(); invalidate()
    }

    private fun pixels(box: FaceBox): RectF {
        val mapped = calibration.map(box).expanded(1.12f)
        return RectF(mapped.left * width, mapped.top * height, mapped.right * width, mapped.bottom * height)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        if (SystemClock.elapsedRealtime() - updatedAt > 500) return
        if (debug) faceRects.forEach { canvas.drawRect(it, linePaint) }
        drawLabels.forEach {
            textPaint.textSize = it.size
            canvas.drawText(it.text, it.bounds.left, it.baseline, textPaint)
            it.cues.forEachIndexed { index, cue ->
                val left = it.bounds.left + index * (it.iconSize + 8f * resources.displayMetrics.density)
                cueBounds.set(left, it.iconTop, left + it.iconSize, it.iconTop + it.iconSize)
                drawCue(canvas, GuestCueIcons.icon(cue.code), cueBounds)
                val markerSize = it.iconSize * 0.36f
                markerBounds.set(cueBounds.right - markerSize, cueBounds.bottom - markerSize, cueBounds.right, cueBounds.bottom)
                drawCue(canvas, GuestCueIcons.marker(cue.sentiment), markerBounds)
            }
        }
    }

    private fun drawCue(canvas: Canvas, resourceId: Int?, bounds: RectF) {
        if (resourceId == null) return
        val drawable = cueDrawables.getOrPut(resourceId) { requireNotNull(AppCompatResources.getDrawable(context, resourceId)).mutate() }
        drawable.setBounds(bounds.left.toInt(), bounds.top.toInt(), bounds.right.toInt(), bounds.bottom.toInt())
        drawable.draw(canvas)
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        layoutLabels()
    }

    private fun layoutLabels() {
        if (width == 0 || height == 0) return
        faceRects = faces.map(::pixels)
        val placed = mutableListOf<DrawLabel>()
        val margin = 8f * resources.displayMetrics.density
        val iconArea = RectF(width - 48f * resources.displayMetrics.density, 0f,
            width.toFloat(), 68f * resources.displayMetrics.density)
        labels.forEach { label ->
            val face = pixels(label.box)
            // Do not pin off-screen people to an unrelated screen edge.
            if (face.centerX() !in 0f..width.toFloat() || face.centerY() !in 0f..height.toFloat()) return@forEach
            val minText = TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_SP, 18f, resources.displayMetrics)
            val maxText = TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_SP, 32f, resources.displayMetrics)
            textPaint.textSize = (face.height() * 0.22f).coerceIn(minText, maxText)
            val text = android.text.TextUtils.ellipsize(label.text, textPaint,
                width * 0.55f, android.text.TextUtils.TruncateAt.END).toString()
            val tw = textPaint.measureText(text)
            val metrics = textPaint.fontMetrics
            val th = metrics.descent - metrics.ascent
            val cues = if (label.text.trim().equals("Unknown", true)) emptyList() else label.cues
                .filter { GuestCueIcons.icon(it.code) != null && GuestCueIcons.marker(it.sentiment) != null }.take(2)
            val iconSize = (textPaint.textSize * 1.6f).coerceIn(40f * resources.displayMetrics.density,
                60f * resources.displayMetrics.density)
            val iconWidth = if (cues.isEmpty()) 0f else cues.size * iconSize + (cues.size - 1) * margin
            val blockWidth = maxOf(tw, iconWidth)
            val blockHeight = th + if (cues.isEmpty()) 0f else margin + iconSize
            val candidates = listOf(
                RectF(face.right + margin, face.top, face.right + margin + blockWidth, face.top + blockHeight),
                RectF(face.left - margin - blockWidth, face.top, face.left - margin, face.top + blockHeight),
                RectF(face.centerX() - blockWidth / 2, face.top - margin - blockHeight, face.centerX() + blockWidth / 2, face.top - margin),
                RectF(face.centerX() - blockWidth / 2, face.bottom + margin, face.centerX() + blockWidth / 2, face.bottom + margin + blockHeight)
            )
            val rect = candidates.firstOrNull { candidate ->
                candidate.left >= margin && candidate.right <= width - margin &&
                    candidate.top >= height * 0.08f && candidate.bottom <= height - margin &&
                    faceRects.none { RectF.intersects(it, candidate) } &&
                    !RectF.intersects(iconArea, candidate) &&
                    placed.none { RectF.intersects(it.bounds, candidate) }
            } ?: return@forEach
            placed.add(DrawLabel(text, rect, textPaint.textSize, rect.top - metrics.ascent, cues,
                iconSize, rect.top + th + margin))
        }
        drawLabels = placed
    }
}
