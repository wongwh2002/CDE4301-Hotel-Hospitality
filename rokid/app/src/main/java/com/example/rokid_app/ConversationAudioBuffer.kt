package com.example.rokid_app

import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder

data class PreferenceGuest(val name: String, val token: String)
data class PreferenceAudio(val captureId: String, val guestToken: String, val wav: ByteArray)

/** One-guest, tap-scoped PCM buffer. Unknown/stale identities never authorize microphone data. */
class ConversationAudioBuffer(private val captureId: String, private val maximumBytes: Int = 90 * 16_000 * 2) {
    private val pcm = ByteArrayOutputStream()
    private val preRoll = ArrayDeque<ByteArray>()
    private var boundName: String? = null
    private var candidateName: String? = null
    private var candidateGeneration = -1L
    private var confirmations = 0
    private var token: String? = null
    private var identityAt = -10_000L
    private var visibleAt = -10_000L
    private var visible = false
    private var closed = false
    private var started = false
    private var speechFrames = 0
    private var lastSpeechByte = 0

    @Synchronized fun observeIdentity(guest: PreferenceGuest, generation: Long, now: Long) {
        if (closed || guest.name.isBlank() || guest.name.equals("Unknown", true) || guest.token.isBlank()) return
        if (boundName != null && boundName != guest.name) { discard(); return }
        confirmations = if (candidateName == guest.name && candidateGeneration == generation && now - identityAt <= 5_000)
            confirmations + 1 else 1
        candidateName = guest.name; candidateGeneration = generation; identityAt = now
        token = guest.token
        if (confirmations >= 2) boundName = guest.name
    }

    @Synchronized fun updateVisibility(guest: RecognizedGuest?, now: Long) {
        visible = guest != null && guest.name == candidateName && guest.generation == candidateGeneration
        visibleAt = now
        if (!visible) preRoll.clear()
    }

    @Synchronized fun append(frame: ShortArray, isSpeech: Boolean, observedAt: Long) {
        if (closed || boundName == null || confirmations < 2 || !visible ||
            observedAt - identityAt !in 0..5_000 || observedAt - visibleAt !in 0..1_000) return
        require(frame.size == 320) { "Expected 20 ms PCM16 frame" }
        val bytes = ByteArray(frame.size * 2)
        ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer().put(frame)
        if (!started) {
            if (!isSpeech) {
                preRoll.addLast(bytes)
                while (preRoll.size > 15) preRoll.removeFirst()
                return
            }
            started = true
            preRoll.forEach { pcm.write(it) }; preRoll.clear()
        }
        if (pcm.size() + bytes.size > maximumBytes) { discard(); return }
        pcm.write(bytes)
        if (isSpeech) { speechFrames++; lastSpeechByte = pcm.size() }
    }

    @Synchronized fun finish(): PreferenceAudio? {
        if (closed) return null
        closed = true
        val binding = token
        if (!started || speechFrames < 25 || binding == null) { pcm.reset(); preRoll.clear(); return null }
        val bytes = pcm.toByteArray()
        val length = minOf(bytes.size, lastSpeechByte + 9_600) // At most 300 ms of trailing silence.
        val result = PreferenceAudio(captureId, binding, wav(bytes, length))
        pcm.reset(); preRoll.clear()
        return result
    }

    @Synchronized fun discard() {
        closed = true; pcm.reset(); preRoll.clear(); token = null; visible = false
    }

    private fun wav(bytes: ByteArray, length: Int): ByteArray {
        val output = ByteBuffer.allocate(44 + length).order(ByteOrder.LITTLE_ENDIAN)
        output.put("RIFF".toByteArray(Charsets.US_ASCII)); output.putInt(36 + length)
        output.put("WAVEfmt ".toByteArray(Charsets.US_ASCII)); output.putInt(16)
        output.putShort(1); output.putShort(1); output.putInt(16_000); output.putInt(32_000)
        output.putShort(2); output.putShort(16); output.put("data".toByteArray(Charsets.US_ASCII)); output.putInt(length)
        output.put(bytes, 0, length)
        return output.array()
    }
}
