package com.example.rokid_app

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View

/** Shape, rather than color alone, conveys status on the monochrome glasses display. */
class ServerStatusView(context: Context, attrs: AttributeSet? = null) : View(context, attrs) {
    enum class State { CONNECTING, ONLINE, OFFLINE }
    var state = State.CONNECTING
        set(value) {
            field = value
            contentDescription = context.getString(when (value) {
                State.CONNECTING -> R.string.server_connecting
                State.ONLINE -> R.string.server_online
                State.OFFLINE -> R.string.server_offline
            })
            invalidate()
        }
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.GREEN; style = Paint.Style.STROKE
        strokeWidth = 1.8f; strokeCap = Paint.Cap.ROUND; strokeJoin = Paint.Join.ROUND
    }

    init { state = State.CONNECTING; importantForAccessibility = IMPORTANT_FOR_ACCESSIBILITY_YES }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.save()
        canvas.scale(width / 28f, height / 28f)
        canvas.drawRoundRect(2f, 3f, 21f, 10f, 1.5f, 1.5f, paint)
        canvas.drawRoundRect(2f, 13f, 21f, 20f, 1.5f, 1.5f, paint)
        canvas.drawPoint(6f, 6.5f, paint)
        canvas.drawPoint(6f, 16.5f, paint)
        when (state) {
            State.ONLINE -> {
                canvas.drawLine(16f, 24f, 20f, 27f, paint)
                canvas.drawLine(20f, 27f, 26f, 20f, paint)
            }
            State.OFFLINE -> {
                canvas.drawLine(18f, 21f, 25f, 27f, paint)
                canvas.drawLine(25f, 21f, 18f, 27f, paint)
            }
            State.CONNECTING -> {
                canvas.drawPoint(15f, 25f, paint)
                canvas.drawPoint(20f, 25f, paint)
                canvas.drawPoint(25f, 25f, paint)
            }
        }
        canvas.restore()
    }
}
