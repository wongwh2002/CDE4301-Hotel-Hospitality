import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from server.app import create_app
from server.audio_preferences import MAX_AUDIO_BYTES, PreferenceService
from server.preference_store import PreferenceStore
from server.test_app import FakeRecognizer, face, jpeg
from server.test_audio_preferences import FakeGemini, FakeWhisper, wav


class PreferenceApiTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.service = PreferenceService(PreferenceStore(Path(self.directory.name)/"test.db"), FakeWhisper(), FakeGemini())
        self.recognizer = FakeRecognizer([face("Ethan")])
        self.client = TestClient(create_app(self.recognizer, preference_service=self.service))
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None,None,None); self.directory.cleanup()

    def binding(self):
        return self.client.post("/detect?request_id=face-1",content=jpeg(),headers={"Content-Type":"image/jpeg"}).json()["preference_guest"]

    def upload(self, token=None, data=None, request_id="capture-1"):
        return self.client.post(f"/audio/preferences?request_id={request_id}",content=wav() if data is None else data,
            headers={"Content-Type":"audio/wav","X-Guest-Token":token or self.binding()["token"]})

    def test_face_bound_audio_persists_and_can_be_retrieved(self):
        binding=self.binding()
        result=self.upload(binding["token"])
        self.assertEqual(result.status_code,200)
        body=result.json(); self.assertEqual(body["name"],"Ethan"); self.assertEqual(body["saved_count"],1)
        self.assertNotIn("transcript",body)
        profile=self.client.get(f"/guests/{body['guest_id']}/preferences").json()
        self.assertEqual(profile["preferences"][0]["key"],"coffee")
        self.assertEqual(len(self.client.get("/guests").json()["guests"]),1)
        self.assertEqual(self.upload(binding["token"]).json(),body)
        self.assertEqual(self.upload(binding["token"],wav(seconds=2)).status_code,409)

    def test_no_binding_for_unknown_or_multiple_faces(self):
        for faces in ([face("Unknown")],[face("Ethan"),face("Alex",x=55)],[]):
            self.recognizer.results=faces
            self.assertIsNone(self.binding())

    def test_name_cannot_replace_the_face_binding(self):
        token=self.binding()["token"]
        response=self.client.post("/audio/preferences?request_id=capture-1&name=Alex",content=wav(),
            headers={"Content-Type":"audio/wav","X-Guest-Token":token})
        self.assertEqual(response.json()["name"],"Ethan")

    def test_invalid_format_token_size_and_missing_id_do_not_write(self):
        token=self.binding()["token"]
        self.assertEqual(self.upload("invalid").status_code,401)
        self.assertEqual(self.upload(token,b"bad").status_code,422)
        self.assertEqual(self.upload(token,b"x"*(MAX_AUDIO_BYTES+1)).status_code,413)
        self.assertEqual(self.client.post("/audio/preferences?request_id=a",content=wav(),headers={"X-Guest-Token":token}).status_code,415)
        self.assertEqual(self.client.get("/guests").json()["guests"],[])
        self.assertEqual(self.upload(token,request_id="bad/id").status_code,422)

    def test_audio_busy_does_not_block_health_or_face_recognition(self):
        token=self.binding()["token"]
        self.service.lock.acquire()
        try:
            self.assertEqual(self.upload(token).status_code,503)
            self.assertEqual(self.client.get("/health").json()["status"],"ready")
            self.assertIsNotNone(self.binding())
        finally: self.service.lock.release()

    def test_missing_key_and_provider_error_are_explicit_without_secret_leaks(self):
        token=self.binding()["token"]
        self.service.extractor.configured=False
        self.assertEqual(self.upload(token).status_code,503)
        self.service.extractor.configured=True
        self.service.extractor.extract=lambda *_: (_ for _ in ()).throw(RuntimeError("secret-provider-message"))
        result=self.upload(token)
        self.assertEqual(result.status_code,502); self.assertEqual(result.json()["detail"]["stage"],"gemini")
        self.assertNotIn("secret-provider-message",result.text)
        self.assertEqual(self.client.get("/guests").json()["guests"],[])
        self.assertFalse(self.service.lock.locked())


if __name__ == "__main__": unittest.main()
