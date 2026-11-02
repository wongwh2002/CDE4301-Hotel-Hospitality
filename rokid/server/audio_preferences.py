"""Audio contract, face-issued guest bindings, and the POC preference pipeline."""
from __future__ import annotations

import hashlib
import io
import logging
import os
import secrets
import threading
import time
import wave
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

from server.audio_models import GeminiExtractor, WhisperTranscriber
from server.preference_store import PreferenceStore

LOG = logging.getLogger("uvicorn.error")
SAMPLE_RATE = 16_000
MAX_AUDIO_SECONDS = 90
MAX_AUDIO_BYTES = SAMPLE_RATE * 2 * MAX_AUDIO_SECONDS + 4096


class GuestBindingError(ValueError):
    pass


class AudioFormatError(ValueError):
    pass


class PipelineError(RuntimeError):
    def __init__(self, stage: str, error: Exception):
        self.stage = stage
        self.provider_code = getattr(error, "code", None)
        super().__init__(f"{stage} processing failed")


class GuestBindings:
    def __init__(self, ttl_seconds=300, maximum=512, clock=time.monotonic):
        self.ttl_seconds, self.maximum, self.clock = ttl_seconds, maximum, clock
        self._tokens: dict[str, tuple[str, float]] = {}
        self._lock = threading.Lock()

    def issue(self, name: str) -> dict:
        if not name.strip() or name.casefold() == "unknown":
            raise GuestBindingError("A recognized guest is required")
        with self._lock:
            now = self.clock()
            self._tokens = {key: value for key, value in self._tokens.items() if value[1] > now}
            while len(self._tokens) >= self.maximum:
                self._tokens.pop(next(iter(self._tokens)))
            token = secrets.token_urlsafe(32)
            self._tokens[token] = (name, now + self.ttl_seconds)
        return {"name": name, "token": token}

    def resolve(self, token: str) -> str:
        with self._lock:
            binding = self._tokens.get(token)
            if binding is None or binding[1] <= self.clock():
                self._tokens.pop(token, None)
                raise GuestBindingError("Guest binding is missing or expired; recognize the guest again")
            return binding[0]


def decode_wav(data: bytes) -> np.ndarray:
    if not 44 <= len(data) <= MAX_AUDIO_BYTES:
        raise AudioFormatError("Audio body is empty or exceeds the 90-second limit")
    try:
        with wave.open(io.BytesIO(data), "rb") as source:
            if (source.getnchannels(), source.getsampwidth(), source.getframerate(), source.getcomptype()) != (1, 2, SAMPLE_RATE, "NONE"):
                raise AudioFormatError("Expected 16 kHz mono PCM16 WAV")
            frames = source.getnframes()
            if not SAMPLE_RATE // 2 <= frames <= SAMPLE_RATE * MAX_AUDIO_SECONDS:
                raise AudioFormatError("Audio must contain 0.5 to 90 seconds")
            pcm = source.readframes(frames)
            if len(pcm) != frames * 2:
                raise AudioFormatError("Truncated WAV audio")
    except (wave.Error, EOFError) as error:
        raise AudioFormatError("Invalid WAV audio") from error
    return np.frombuffer(pcm, dtype="<i2").astype(np.float32) / 32768.0


class PreferenceService:
    def __init__(self, store: PreferenceStore, transcriber=None, extractor=None, bindings=None):
        self.store = store
        self.transcriber = transcriber or WhisperTranscriber()
        self.extractor = extractor or GeminiExtractor()
        self.bindings = bindings or GuestBindings()
        self.lock = threading.Lock()

    @classmethod
    def from_environment(cls):
        load_dotenv(Path(__file__).parent / ".env", override=False)
        return cls(PreferenceStore(Path(os.getenv("PREFERENCES_DB", str(Path(__file__).parent / "data" / "preferences.sqlite3")))))

    def health(self):
        return {"enabled": True, "whisper_model": self.transcriber.model_name,
                "gemini_model": self.extractor.model_name, "gemini_configured": self.extractor.configured}

    def process(self, data: bytes, token: str, capture_id: str) -> dict:
        name = self.bindings.resolve(token)
        digest = hashlib.sha256(data).hexdigest()
        existing = self.store.existing_capture(capture_id, name, digest)
        if existing:
            return existing
        pcm = decode_wav(data)
        started = time.perf_counter()
        try:
            transcript = self.transcriber.transcribe(pcm)
        except Exception as error:
            raise PipelineError("whisper", error) from None
        transcribed = time.perf_counter()
        try:
            preferences = self.extractor.extract(transcript, name) if transcript.strip() else []
        except Exception as error:
            raise PipelineError("gemini", error) from None
        extracted = time.perf_counter()
        timings = {"audio_seconds": round(len(pcm) / SAMPLE_RATE, 3),
                   "whisper_ms": round((transcribed-started)*1000, 1),
                   "gemini_ms": round((extracted-transcribed)*1000, 1)}
        result = self.store.save(capture_id, name, digest, preferences, timings)
        LOG.info("Preference capture %s completed saved_count=%d whisper_ms=%.1f gemini_ms=%.1f",
                 capture_id, len(preferences), timings["whisper_ms"], timings["gemini_ms"])
        return result

    def close(self):
        close = getattr(self.extractor, "close", None)
        if close:
            close()
