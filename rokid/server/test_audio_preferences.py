import io
import tempfile
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from server.audio_models import Extraction, GeminiExtractor, Preference, supported_preferences
from server.audio_preferences import GuestBindings, GuestBindingError, PreferenceService, decode_wav
from server.preference_store import CaptureConflict, PreferenceStore


def wav(seconds=1, rate=16000, channels=1):
    output = io.BytesIO()
    with wave.open(output, "wb") as audio:
        audio.setnchannels(channels); audio.setsampwidth(2); audio.setframerate(rate)
        audio.writeframes(b"\0\0" * int(rate * seconds) * channels)
    return output.getvalue()


class FakeWhisper:
    model_name = "test"
    def __init__(self): self.calls = 0
    def transcribe(self, pcm):
        self.calls += 1
        return "Ethan prefers black coffee without sugar."


class FakeGemini:
    model_name = "test"
    configured = True
    def extract(self, transcript, name):
        return [{"key": "coffee", "value": "Black coffee without sugar", "evidence": "black coffee without sugar"}]


class AudioContractTests(unittest.TestCase):
    def test_wav_format_limits_and_truncation(self):
        self.assertEqual(decode_wav(wav()).shape, (16000,))
        for invalid in (b"bad", wav(rate=8000), wav(channels=2), wav(seconds=0.1), wav()[:-20], wav(seconds=91)):
            with self.subTest(size=len(invalid)), self.assertRaises(ValueError): decode_wav(invalid)

    def test_guest_token_expires_and_unknown_is_rejected(self):
        now = [1.0]
        bindings = GuestBindings(ttl_seconds=5, maximum=1, clock=lambda: now[0])
        first = bindings.issue("Ethan")
        self.assertEqual(bindings.resolve(first["token"]), "Ethan")
        bindings.issue("Alex")
        with self.assertRaises(GuestBindingError): bindings.resolve(first["token"])
        token = bindings.issue("Ethan")["token"]; now[0] = 6.0
        with self.assertRaises(GuestBindingError): bindings.resolve(token)
        with self.assertRaises(GuestBindingError): bindings.issue("Unknown")

    def test_only_evidence_supported_facts_are_saved(self):
        extraction = Extraction(preferences=[Preference(key="coffee", value="Black", evidence="black coffee"),
            Preference(key="room_view", value="Ocean", evidence="ocean view")])
        self.assertEqual([p["key"] for p in supported_preferences(extraction,"I prefer black coffee.")], ["coffee"])

    def test_gemini_retries_transient_errors_once_without_fabricating_facts(self):
        class Busy(Exception): code=503
        model=GeminiExtractor(api_key="test-only")
        generate=Mock(side_effect=[Busy(),SimpleNamespace(text='{"preferences":[{"key":"coffee","value":"Black","evidence":"black coffee"}]}')])
        model._client=SimpleNamespace(models=SimpleNamespace(generate_content=generate))
        with patch("server.audio_models.time.sleep"):
            self.assertEqual(model.extract("The guest prefers black coffee.","Test Guest")[0]["key"],"coffee")
        self.assertEqual(generate.call_count,2)
        generate.reset_mock(); generate.side_effect=Busy()
        with patch("server.audio_models.time.sleep"),self.assertRaises(Busy): model.extract("black coffee","Test Guest")
        self.assertEqual(generate.call_count,2)


class PreferencePipelineTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.store = PreferenceStore(Path(self.directory.name) / "preferences.db")
        self.whisper = FakeWhisper()
        self.service = PreferenceService(self.store, self.whisper, FakeGemini())
        self.token = self.service.bindings.issue("Ethan")["token"]

    def tearDown(self): self.directory.cleanup()

    def test_pipeline_is_durable_idempotent_and_guest_specific(self):
        result = self.service.process(wav(), self.token, "capture-1")
        self.assertEqual(result["saved_count"], 1)
        self.assertEqual(self.service.process(wav(), self.token, "capture-1"), result)
        self.assertEqual(self.whisper.calls, 1)
        reopened = PreferenceStore(self.store.path)
        self.assertEqual(reopened.guests()[0]["preferences"][0]["value"], "Black coffee without sugar")
        with self.assertRaises(CaptureConflict): self.service.process(wav(seconds=2), self.token, "capture-1")
        other = self.service.bindings.issue("Alex")["token"]
        with self.assertRaises(CaptureConflict): self.service.process(wav(), other, "capture-1")

    def test_latest_preference_replaces_previous_without_duplicate_rows(self):
        for index, value in enumerate(("Black", "With milk")):
            self.store.save(str(index), "Ethan", str(index), [{"key":"coffee","value":value,"evidence":value}], {})
        self.assertEqual(len(self.store.guests()[0]["preferences"]), 1)
        self.assertEqual(self.store.guests()[0]["preferences"][0]["value"], "With milk")

    def test_failure_cannot_partially_write_a_profile(self):
        self.service.extractor.extract = lambda *_: (_ for _ in ()).throw(RuntimeError("provider unavailable"))
        with self.assertRaises(RuntimeError): self.service.process(wav(), self.token, "capture-1")
        self.assertEqual(self.store.guests(), [])

    def test_unknown_audio_never_reaches_whisper(self):
        with self.assertRaises(GuestBindingError): self.service.process(wav(), "wrong", "capture-1")
        self.assertEqual(self.whisper.calls, 0)

    def test_empty_transcript_saves_no_preferences_and_skips_gemini(self):
        self.whisper.transcribe = lambda _: ""
        self.service.extractor.extract = lambda *_: self.fail("Gemini must not receive silence")
        self.assertEqual(self.service.process(wav(), self.token, "capture-1")["saved_count"], 0)


if __name__ == "__main__": unittest.main()
