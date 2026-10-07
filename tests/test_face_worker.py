"""Tests for face-worker service."""

import base64
from fixtures.synthetic_data import SYNTHETIC_JPEG_BYTES


def test_face_worker_health(face_worker_client):
    """Test health endpoint."""
    resp = face_worker_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "face-worker"


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
        "X-Captured-At": "2026-10-07T12:00:00Z",
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
    import importlib.util
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent
    worker_path = repo_root / "apps" / "face-worker" / "worker.py"
    spec = importlib.util.spec_from_file_location("face_worker_queue_test", worker_path)
    worker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(worker)
    monkeypatch.setattr(worker, "QUEUE_MAXSIZE", 2)

    stream_id = "queue-bound-test"
    for sequence in range(3):
        worker.enqueue_frame(stream_id, "device-test-1", sequence, "now", bytes([sequence]))

    queue = worker._stream_queues[stream_id]
    assert len(queue) == 2
    assert queue[-1][-1] == b"\x02"
    assert worker.get_stats()["frames_dropped"] == 1
