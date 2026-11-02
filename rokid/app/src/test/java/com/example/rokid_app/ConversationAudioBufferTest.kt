package com.example.rokid_app

import org.junit.Assert.*
import org.junit.Test
import java.nio.ByteBuffer
import java.nio.ByteOrder

class ConversationAudioBufferTest {
    private val frame=ShortArray(320) { 1234 }
    private fun authorize(buffer: ConversationAudioBuffer, name: String="Ethan", generation: Long=1, now: Long=1000) {
        buffer.observeIdentity(PreferenceGuest(name,"token"),generation,now)
        buffer.observeIdentity(PreferenceGuest(name,"token"),generation,now+100)
        buffer.updateVisibility(RecognizedGuest(name,generation),now+100)
    }
    private fun speech(buffer: ConversationAudioBuffer, now: Long=1200) { repeat(30) { buffer.append(frame,true,now) } }

    @Test fun unknownOrSingleRecognitionNeverProducesAnUpload() {
        for (recognized in 0..1) {
            val buffer=ConversationAudioBuffer("id")
            if (recognized==1) { buffer.observeIdentity(PreferenceGuest("Ethan","token"),1,1000); buffer.updateVisibility(RecognizedGuest("Ethan",1),1000) }
            speech(buffer); assertNull(buffer.finish())
        }
    }
    @Test fun stableIdentityProducesValidLittleEndianWavAndOnlyFinishesOnce() {
        val buffer=ConversationAudioBuffer("capture"); authorize(buffer); speech(buffer)
        val audio=buffer.finish()!!
        assertEquals("capture",audio.captureId); assertEquals("token",audio.guestToken)
        val bytes=ByteBuffer.wrap(audio.wav).order(ByteOrder.LITTLE_ENDIAN)
        assertEquals("RIFF",String(audio.wav,0,4,Charsets.US_ASCII)); assertEquals(16000,bytes.getInt(24))
        assertEquals(1234,bytes.getShort(44).toInt()); assertEquals(audio.wav.size-44,bytes.getInt(40))
        assertNull(buffer.finish())
    }
    @Test fun changingGuestsAbortsTheWholeCapture() {
        val buffer=ConversationAudioBuffer("id"); authorize(buffer); speech(buffer)
        buffer.observeIdentity(PreferenceGuest("Alex","other-token"),2,1300)
        assertNull(buffer.finish())
    }
    @Test fun staleOrInvisibleGuestCannotAuthorizeNewAudio() {
        for (invisible in listOf(false,true)) {
            val buffer=ConversationAudioBuffer("id"); authorize(buffer)
            if (invisible) buffer.updateVisibility(null,1200)
            speech(buffer,if(invisible) 1300 else 10_000)
            assertNull(buffer.finish())
        }
    }
    @Test fun silenceOnlyAndShortClicksDoNotUpload() {
        val buffer=ConversationAudioBuffer("id"); authorize(buffer)
        repeat(50) { buffer.append(frame,false,1200) }; buffer.append(frame,true,1200)
        assertNull(buffer.finish())
    }
    @Test fun trailingSilenceIsTrimmedAndAudioIsBounded() {
        val buffer=ConversationAudioBuffer("id"); authorize(buffer); speech(buffer)
        repeat(100) { buffer.append(frame,false,1200) }
        assertEquals(44+(30+15)*640,buffer.finish()!!.wav.size)
        val limited=ConversationAudioBuffer("id",maximumBytes=640*20); authorize(limited); speech(limited)
        assertNull(limited.finish())
    }
    @Test fun explicitDiscardAndReacquiredTrackRequireFreshConfirmation() {
        val buffer=ConversationAudioBuffer("id"); authorize(buffer); buffer.discard(); speech(buffer); assertNull(buffer.finish())
        val next=ConversationAudioBuffer("next"); authorize(next)
        next.observeIdentity(PreferenceGuest("Ethan","new-token"),2,1300)
        next.updateVisibility(RecognizedGuest("Ethan",2),1300); speech(next,1400)
        assertNull(next.finish())
    }
}
