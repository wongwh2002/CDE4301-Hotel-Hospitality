"""Tests for face-worker service."""

import asyncio
import base64
import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from fixtures.synthetic_data import SYNTHETIC_JPEG_BYTES


def test_face_worker_health(face_worker_client):
    """Test health endpoint."""
    resp = face_worker_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "face-worker"
    assert data["requested_execution_provider"] == "cpu"
    assert data["service_startup_ms"] is not None
    assert data["model_initialization_ms"] is None
    assert isinstance(data["model_cache_warm_at_start"], bool)
    assert data["model_runtime"] is None
    assert data["match_threshold"] == 0.65
    assert data["stable_frame_count"] == 3
    assert data["stable_match_count"] == 2


def test_internal_face_worker_routes_require_service_token(face_worker_client):
    response = face_worker_client.get(
        "/internal/v1/candidates",
        headers={"X-Internal-Token": "wrong-token"},
    )
    assert response.status_code == 401


def test_candidate_enrollment_lifecycle(face_worker_client):
    """Test candidate presence lifecycle; reference-photo bytes are discarded."""
    candidate_id = "cand-test-001"
    photo_b64 = base64.b64encode(SYNTHETIC_JPEG_BYTES).decode()

    # 1. Enroll candidate
    enroll_payload = {
        "candidate_id": candidate_id,
        "expires_at": "2099-01-01T00:00:00Z",
        "photo_b64": photo_b64,
    }
    resp = face_worker_client.put(f"/internal/v1/candidates/{candidate_id}", json=enroll_payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "enrolled"

    # 2. Repeated enrollment is safe (idempotent)
    resp_repeated = face_worker_client.put(f"/internal/v1/candidates/{candidate_id}", json=enroll_payload)
    assert resp_repeated.status_code == 200

    # 3. Verify in active list
    resp_list = face_worker_client.get("/internal/v1/candidates")
    assert resp_list.status_code == 200
    assert candidate_id in resp_list.json()

    # 4. Delete candidate
    resp_del = face_worker_client.delete(f"/internal/v1/candidates/{candidate_id}")
    assert resp_del.status_code == 200
    assert resp_del.json()["status"] == "removed"

    # 5. Verify gone from active list
    resp_list2 = face_worker_client.get("/internal/v1/candidates")
    assert candidate_id not in resp_list2.json()


def test_frame_intake_valid_jpeg(face_worker_client):
    """Test 202 Accepted on valid JPEG frame."""
    headers = {
        "Content-Type": "image/jpeg",
        "X-Stream-Id": "stream-test-1",
        "X-Device-Id": "device-test-1",
        "X-Sequence": "1",
        "X-Captured-At": datetime.now(timezone.utc).isoformat(),
    }
    resp = face_worker_client.post(
        "/internal/v1/frames",
        content=SYNTHETIC_JPEG_BYTES,
        headers=headers,
    )
    assert resp.status_code == 202
    data = resp.json()
    assert data["status"] == "accepted"
    assert data["stream_id"] == "stream-test-1"


def test_frame_intake_missing_stream_id(face_worker_client):
    """Test 400 Bad Request when X-Stream-Id is omitted."""
    resp = face_worker_client.post(
        "/internal/v1/frames",
        content=SYNTHETIC_JPEG_BYTES,
        headers={"Content-Type": "image/jpeg"},
    )
    assert resp.status_code == 400


def test_frame_intake_rejects_invalid_stream_id(face_worker_client):
    resp = face_worker_client.post(
        "/internal/v1/frames",
        content=SYNTHETIC_JPEG_BYTES,
        headers={
            "Content-Type": "image/jpeg",
            "X-Stream-Id": "../guest",
            "X-Device-Id": "device-test-1",
        },
    )
    assert resp.status_code == 400


def test_frame_intake_requires_jpeg_content_type(face_worker_client):
    resp = face_worker_client.post(
        "/internal/v1/frames",
        content=SYNTHETIC_JPEG_BYTES,
        headers={
            "Content-Type": "application/octet-stream",
            "X-Stream-Id": "stream-test-1",
            "X-Device-Id": "device-test-1",
        },
    )
    assert resp.status_code == 415


def test_frame_intake_accepts_jpeg_xl(face_worker_client):
    import imagecodecs
    import numpy as np

    sample = np.zeros((16, 24, 3), dtype=np.uint8)
    sample[:, :, 0] = 40
    frame = imagecodecs.jpegxl_encode(sample, lossless=True)
    response = face_worker_client.post(
        "/internal/v1/frames",
        content=frame,
        headers={
            "Content-Type": "image/jxl",
            "X-Stream-Id": "stream-jxl-test",
            "X-Device-Id": "device-jxl-test",
            "X-Sequence": "1",
            "X-Captured-At": datetime.now(timezone.utc).isoformat(),
        },
    )

    assert response.status_code == 202
    assert response.json()["status"] == "accepted"


def test_jpeg_xl_decoder_returns_bgr_pixels():
    import imagecodecs
    import numpy as np

    from vision import InsightFaceEngine

    rgb = np.zeros((3, 4, 3), dtype=np.uint8)
    rgb[0, 0] = [11, 73, 201]
    encoded = imagecodecs.jpegxl_encode(rgb, lossless=True)

    decoded = InsightFaceEngine._decode(encoded, "image/jxl")

    assert decoded.shape == (3, 4, 3)
    assert decoded.dtype == np.uint8
    assert decoded[0, 0].tolist() == [201, 73, 11]


def test_jpeg_xl_decoder_expands_grayscale_to_bgr():
    import imagecodecs
    import numpy as np

    from vision import InsightFaceEngine

    gray = np.full((3, 4), 83, dtype=np.uint8)
    encoded = imagecodecs.jpegxl_encode(gray, lossless=True)

    decoded = InsightFaceEngine._decode(encoded, "image/jxl")

    assert decoded.shape == (3, 4, 3)
    assert decoded[0, 0].tolist() == [83, 83, 83]


def test_frame_intake_rejects_malformed_jpeg_xl(face_worker_client):
    response = face_worker_client.post(
        "/internal/v1/frames",
        content=b"not a JPEG XL frame",
        headers={
            "Content-Type": "image/jxl",
            "X-Stream-Id": "stream-jxl-invalid",
            "X-Device-Id": "device-jxl-test",
        },
    )

    assert response.status_code == 400
    assert "Malformed JPEG XL" in response.json()["detail"]


def test_frame_intake_malformed_jpeg(face_worker_client):
    """Test 400 Bad Request on invalid/corrupted frame bytes."""
    corrupted_bytes = b"not a valid jpeg frame"
    headers = {
        "Content-Type": "image/jpeg",
        "X-Stream-Id": "stream-test-1",
        "X-Device-Id": "device-test-1",
    }
    resp = face_worker_client.post(
        "/internal/v1/frames",
        content=corrupted_bytes,
        headers=headers,
    )
    assert resp.status_code == 400
    assert "Malformed JPEG frame" in resp.json()["detail"]


def test_frame_intake_oversized_payload(face_worker_client):
    """Test 413 Payload Too Large on oversized frame."""
    # Build oversized payload with valid JPEG SOI/EOI
    # MAX_FRAME_SIZE_BYTES set to 1048576 in conftest
    oversized = b"\xff\xd8" + (b"\x00" * (1048576 + 10)) + b"\xff\xd9"
    headers = {
        "Content-Type": "image/jpeg",
        "X-Stream-Id": "stream-test-1",
        "X-Device-Id": "device-test-1",
    }
    resp = face_worker_client.post(
        "/internal/v1/frames",
        content=oversized,
        headers=headers,
    )
    assert resp.status_code == 413


def test_face_worker_queue_is_bounded_and_keeps_latest_frame(monkeypatch):
    repo_root = Path(__file__).resolve().parent.parent
    worker_path = repo_root / "apps" / "face-worker" / "worker.py"
    spec = importlib.util.spec_from_file_location("face_worker_queue_test", worker_path)
    worker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(worker)
    monkeypatch.setattr(worker, "QUEUE_MAXSIZE", 2)

    stream_id = "queue-bound-test"
    for sequence in range(3):
        worker.enqueue_frame(
            stream_id,
            "device-test-1",
            sequence,
            "now",
            bytes([sequence]),
            image_format="image/jxl",
        )

    queue = worker._stream_queues[stream_id]
    assert len(queue) == 2
    assert queue[-1][-2] == "image/jxl"
    assert queue[-1][-1] == b"\x02"
    assert worker.get_stats()["frames_dropped"] == 1


def test_worker_keeps_multiple_tracks_and_sends_only_changed_crops(monkeypatch):
    repo_root = Path(__file__).resolve().parent.parent
    worker_path = repo_root / "apps" / "face-worker" / "worker.py"
    spec = importlib.util.spec_from_file_location("face_worker_multiface_test", worker_path)
    worker = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = worker
    spec.loader.exec_module(worker)

    now = [100.0]
    monkeypatch.setattr(worker.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(worker, "STABLE_FRAME_COUNT", 2)
    monkeypatch.setattr(worker, "STABLE_REFRESH_INTERVAL_SECONDS", 1.0)
    monkeypatch.setattr(worker, "CROP_CHANGE_HAMMING_DISTANCE", 8)

    left_embedding = object()
    right_embedding = object()

    class MatchingEngine:
        @staticmethod
        def cosine_similarity(query, reference):
            return 0.95 if query is reference else 0.05

    worker.set_face_engine(MatchingEngine())
    worker._candidates["cand-01"] = worker.CandidateState(
        expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
        embeddings=[left_embedding],
        template_status="ready",
    )
    worker._candidates["cand-02"] = worker.CandidateState(
        expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
        embeddings=[right_embedding],
        template_status="ready",
    )
    faces = [
        SimpleNamespace(
            bbox=(10.0, 10.0, 40.0, 40.0),
            embedding=left_embedding,
            crop_jpeg=b"\xff\xd8alex\xff\xd9",
            crop_signature=0,
        ),
        SimpleNamespace(
            bbox=(100.0, 10.0, 40.0, 40.0),
            embedding=right_embedding,
            crop_jpeg=b"\xff\xd8jordan\xff\xd9",
            crop_signature=0,
        ),
    ]

    assert worker._process_frame("phone-1", "stream-1", faces) == []
    matches = worker._process_frame("phone-1", "stream-1", faces)
    assert len(matches) == 2
    assert {event["status"] for event in matches} == {"stable_match"}
    assert len({event["track_id"] for event in matches}) == 2
    assert all(event["crop_id"].startswith("crop-") for event in matches)
    assert all(event["crop_b64"] for event in matches)
    matches_by_crop = {event["crop_b64"]: event for event in matches}
    alex_crop = base64.b64encode(b"\xff\xd8alex\xff\xd9").decode()
    jordan_crop = base64.b64encode(b"\xff\xd8jordan\xff\xd9").decode()
    assert matches_by_crop[alex_crop]["candidate_id"] == "cand-01"
    assert matches_by_crop[jordan_crop]["candidate_id"] == "cand-02"
    for event in matches:
        worker._set_crop_delivery_state(
            "stream-1", event["track_id"], event["crop_id"], delivered=True
        )

    # One unchanged crop refreshes the TTL without retransmitting its image;
    # a perceptually changed crop waits for the one-second refresh boundary.
    changed_faces = [faces[0], SimpleNamespace(
        bbox=faces[1].bbox,
        embedding=faces[1].embedding,
        crop_jpeg=b"\xff\xd8jordan-new\xff\xd9",
        crop_signature=0xFF,
    )]
    now[0] += 0.2
    assert worker._process_frame("phone-1", "stream-1", changed_faces) == []
    now[0] += 0.9
    refreshes = worker._process_frame("phone-1", "stream-1", changed_faces)
    assert len(refreshes) == 2
    assert {event["status"] for event in refreshes} == {"stable_refresh"}
    unchanged, changed = refreshes
    assert "crop_b64" not in unchanged
    assert unchanged["crop_id"] == matches[0]["crop_id"]
    assert changed["crop_b64"]
    assert changed["crop_id"] != matches[1]["crop_id"]


def test_worker_retries_crop_until_lounge_control_confirms_delivery(monkeypatch):
    repo_root = Path(__file__).resolve().parent.parent
    worker_path = repo_root / "apps" / "face-worker" / "worker.py"
    spec = importlib.util.spec_from_file_location("face_worker_crop_retry_test", worker_path)
    worker = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = worker
    spec.loader.exec_module(worker)

    now = [100.0]
    monkeypatch.setattr(worker.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(worker, "STABLE_FRAME_COUNT", 2)
    monkeypatch.setattr(worker, "STABLE_REFRESH_INTERVAL_SECONDS", 1.0)

    class MatchingEngine:
        @staticmethod
        def cosine_similarity(_query, _reference):
            return 0.95

    worker.set_face_engine(MatchingEngine())
    worker._candidates["cand-01"] = worker.CandidateState(
        expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
        embeddings=[object()],
        template_status="ready",
    )
    face = SimpleNamespace(
        bbox=(10.0, 10.0, 40.0, 40.0),
        embedding=object(),
        crop_jpeg=b"\xff\xd8alex\xff\xd9",
        crop_signature=0,
    )
    worker._process_frame("phone-1", "stream-retry", [face])
    first = worker._process_frame("phone-1", "stream-retry", [face])[0]
    assert first["status"] == "stable_match"
    assert first["crop_b64"]

    class FailedClient:
        async def post(self, *_args, **_kwargs):
            raise worker.httpx.ConnectError("lounge-control offline")

    class SuccessResponse:
        status_code = 200

        def raise_for_status(self):
            return None

        @staticmethod
        def json():
            return {"crop_delivered": True}

    class SuccessfulClient:
        async def post(self, *_args, **_kwargs):
            return SuccessResponse()

    asyncio.run(worker._report_events(FailedClient(), [first]))
    assert worker._tracks["stream-retry"][first["track_id"]].crop_pending

    now[0] += 1.1
    retry = worker._process_frame("phone-1", "stream-retry", [face])[0]
    assert retry["status"] == "stable_refresh"
    assert retry["crop_id"] == first["crop_id"]
    assert retry["crop_b64"] == first["crop_b64"]
    asyncio.run(worker._report_events(SuccessfulClient(), [retry]))
    assert not worker._tracks["stream-retry"][first["track_id"]].crop_pending

    now[0] += 1.1
    delivered_refresh = worker._process_frame("phone-1", "stream-retry", [face])[0]
    assert "crop_b64" not in delivered_refresh
