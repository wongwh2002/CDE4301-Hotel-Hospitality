import io
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from server.app import FaceResult, MAX_BYTES, create_app


class FakeRecognizer:
    def __init__(self, results=None):
        self.results = results or []
        self.seen_size = None

    def detect(self, image):
        self.seen_size = (image.shape[1], image.shape[0])
        return self.results


def jpeg():
    output = io.BytesIO()
    Image.new("RGB", (120, 80), "white").save(output, "JPEG")
    return output.getvalue()


def face(name="Ping Hui", score=0.61, x=10):
    return FaceResult(
        name, score,
        {"x": x, "y": 12, "width": 30, "height": 40},
        0.97,
    )


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.recognizer = FakeRecognizer()
        self.app = create_app(self.recognizer, threshold=0.363)
        self.client = TestClient(self.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def send(self, content=None, rotation=0):
        return self.client.post(
            f"/detect?request_id=test-1&rotation={rotation}",
            content=jpeg() if content is None else content,
            headers={"Content-Type": "image/jpeg"},
        )

    def test_ready_uses_protocol_v2(self):
        result = self.client.get("/health").json()
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["protocol_version"], 2)
        self.assertEqual(result["match_threshold"], 0.363)

    def test_names_scores_boxes_and_request_correlation(self):
        self.recognizer.results = [face(), face(x=55)]
        result = self.send().json()
        self.assertEqual(result["display"], "Ping Hui x2")
        self.assertEqual(len(result["faces"]), 2)
        self.assertEqual(result["faces"][0]["name"], "Ping Hui")
        self.assertEqual(result["faces"][0]["similarity"], 0.61)
        self.assertEqual(result["faces"][0]["box"], {"x": 10, "y": 12, "width": 30, "height": 40})
        self.assertEqual(result["request_id"], "test-1")
        self.assertEqual(result["protocol_version"], 2)
        self.assertEqual(self.recognizer.seen_size, (120, 80))

    def test_unrecognized_and_no_face_results(self):
        self.recognizer.results = [face("Unknown", 0.2)]
        self.assertEqual(self.send().json()["display"], "Unknown")
        self.recognizer.results = []
        result = self.send().json()
        self.assertEqual(result["display"], "No face detected")
        self.assertEqual(result["faces"], [])

    def test_logs_similarity_without_calling_it_percent_confidence(self):
        self.recognizer.results = [face()]
        with self.assertLogs("uvicorn.error", level="INFO") as captured:
            self.send()
        self.assertTrue(any("Ping Hui" in line and "cosine similarity 0.610" in line for line in captured.output))

    def test_full_frame_rotation(self):
        for rotation, dimensions in [(0, (120, 80)), (90, (80, 120)), (180, (120, 80)), (270, (80, 120))]:
            with self.subTest(rotation=rotation):
                self.assertEqual(self.send(rotation=rotation).status_code, 200)
                self.assertEqual(self.recognizer.seen_size, dimensions)

    def test_invalid_rotation(self):
        self.assertEqual(self.send(rotation=45).status_code, 422)

    def test_invalid_images_release_lock(self):
        self.assertEqual(self.send(b"not an image").status_code, 400)
        self.assertEqual(self.send(b"").status_code, 400)
        self.assertEqual(self.send().status_code, 200)

    def test_wrong_media_type_and_oversized_body(self):
        self.assertEqual(self.client.post("/detect?request_id=test", content=b"x").status_code, 415)
        self.assertEqual(self.send(b"x" * (MAX_BYTES + 1)).status_code, 413)

    def test_busy_returns_immediately(self):
        self.app.state.inference_lock.acquire()
        try:
            self.assertEqual(self.send().status_code, 503)
        finally:
            self.app.state.inference_lock.release()

    def test_recognizer_error_releases_lock(self):
        self.recognizer.detect = lambda image: (_ for _ in ()).throw(RuntimeError("test failure"))
        self.assertEqual(self.send().status_code, 500)
        self.recognizer.detect = lambda image: []
        self.assertEqual(self.send().status_code, 200)

    def test_invalid_match_threshold(self):
        with self.assertRaises(ValueError):
            create_app(self.recognizer, threshold=1.1)


if __name__ == "__main__":
    unittest.main()
