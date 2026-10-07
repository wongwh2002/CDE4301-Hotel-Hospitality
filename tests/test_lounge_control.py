"""Tests for lounge-control service."""

import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from starlette.websockets import WebSocketDisconnect
from fixtures.synthetic_data import SYNTHETIC_JPEG_BYTES


def test_lounge_control_health(lounge_control_client):
    """Test health endpoint."""
    resp = lounge_control_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "lounge-control"


def test_active_cohort_empty_initially(lounge_control_client):
    """Test active cohort endpoint."""
    resp = lounge_control_client.get("/v1/lounge/cohort")
    assert resp.status_code == 200
    data = resp.json()
    assert "active_candidates" in data
    assert "total_active" in data


@pytest.mark.asyncio
async def test_post_tap_entry_and_exit(lounge_control_client):
    """Test full card tap lifecycle (entry, idempotency, exit)."""
    # Mock external HTTP responses for mock-hotel and face-worker
    mock_profile_resp = MagicMock()
    mock_profile_resp.status_code = 200
    mock_profile_resp.json.return_value = {
        "guest_ref": "guest-alex-101",
        "display_name": "Alex",
        "room_number": "401",
        "allergies": ["Peanut allergy"],
        "preferences": ["Sparkling water"],
    }

    mock_photo_resp = MagicMock()
    mock_photo_resp.status_code = 200
    mock_photo_resp.content = SYNTHETIC_JPEG_BYTES

    mock_worker_put_resp = MagicMock()
    mock_worker_put_resp.status_code = 200

    mock_worker_del_resp = MagicMock()
    mock_worker_del_resp.status_code = 200

    async def mock_get(url, *args, **kwargs):
        if "lounge-profile" in url:
            return mock_profile_resp
        elif "photo" in url:
            return mock_photo_resp
        raise ValueError(f"Unexpected GET {url}")

    async def mock_put(url, *args, **kwargs):
        return mock_worker_put_resp

    async def mock_delete(url, *args, **kwargs):
        return mock_worker_del_resp

    with patch("apps_lounge_control.http_client") as mock_client:
        mock_client.get = AsyncMock(side_effect=mock_get)
        mock_client.put = AsyncMock(side_effect=mock_put)
        mock_client.delete = AsyncMock(side_effect=mock_delete)

        # 1. Post entry tap
        entry_tap = {
            "event_id": "evt-unique-001",
            "reader_id": "lounge-entry-1",
            "guest_ref": "guest-alex-101",
            "event_type": "entry",
            "occurred_at": "2026-10-07T12:00:00Z",
        }
        resp = lounge_control_client.post("/v1/lounge/taps", json=entry_tap)
        assert resp.status_code == 200
        data = resp.json()
        assert data["action"] == "admitted"
        assert "guest_ref" not in data
        assert "display_name" not in data
        assert "room_number" not in data
        candidate_id = data["candidate_id"]

        # 2. Test idempotency with duplicate tap
        resp_idempotent = lounge_control_client.post("/v1/lounge/taps", json=entry_tap)
        assert resp_idempotent.status_code == 200
        assert resp_idempotent.json().get("idempotent") is True

        # 3. Post exit tap
        exit_tap = {
            "event_id": "evt-unique-002",
            "reader_id": "lounge-entry-1",
            "guest_ref": "guest-alex-101",
            "event_type": "exit",
            "occurred_at": "2026-10-07T12:30:00Z",
        }
        resp_exit = lounge_control_client.post("/v1/lounge/taps", json=exit_tap)
        assert resp_exit.status_code == 200
        data_exit = resp_exit.json()
        assert data_exit["action"] == "departed"
        assert candidate_id in data_exit["removed_candidates"]


def test_device_websocket_authentication_failure(lounge_control_client):
    """Test unauthorized WebSocket is closed with WS_1008_POLICY_VIOLATION."""
    # Attempt connect with invalid token
    with pytest.raises(WebSocketDisconnect) as excinfo:
        with lounge_control_client.websocket_connect(
            "/v1/devices/device-test-1/stream?token=invalid-secret"
        ) as ws:
            ws.receive_json()
    assert excinfo.value.code == 1008


def test_internal_match_callback_requires_service_token(lounge_control_client):
    payload = {
        "candidate_id": "cand-opaque-001",
        "stream_id": "stream-01",
        "track_id": "track-01",
        "status": "stable_match",
        "confidence": 0.9,
        "matched_at": "2026-10-07T12:00:00Z",
    }
    response = lounge_control_client.post(
        "/internal/v1/matches",
        json=payload,
        headers={"X-Internal-Token": "wrong-token"},
    )
    assert response.status_code == 401


def test_one_control_routes_cues_to_multiple_phone_sessions(lounge_control_client):
    from apps_lounge_control import cohort_manager, device_manager

    for candidate_id, guest_ref, display_name in (
        ("cand-phone-a", "guest-alex-101", "Alex"),
        ("cand-phone-b", "guest-jordan-102", "Jordan"),
    ):
        cohort_manager.admit_candidate(
            candidate_id=candidate_id,
            guest_ref=guest_ref,
            display_name=display_name,
            room_number=None,
            allergies=[],
            preferences=[],
            expires_at="2099-01-01T00:00:00Z",
        )

    with lounge_control_client.websocket_connect(
        "/v1/devices/phone-a/stream?token=test-secret-token"
    ) as phone_a, lounge_control_client.websocket_connect(
        "/v1/devices/phone-b/stream?token=test-secret-token"
    ) as phone_b:
        assert phone_a.receive_json()["type"] == "session_ack"
        assert phone_b.receive_json()["type"] == "session_ack"

        for ws, stream_id in ((phone_a, "stream-a"), (phone_b, "stream-b")):
            ws.send_json({
                "type": "frame_meta",
                "stream_id": stream_id,
                "sequence": 1,
                "captured_at": "2026-10-07T12:00:00Z",
            })
            ws.send_json({"type": "ping"})
            assert ws.receive_json()["type"] == "pong"

        assert device_manager.connected_count() == 2
        for candidate_id, stream_id, display_name in (
            ("cand-phone-a", "stream-a", "ALEX"),
            ("cand-phone-b", "stream-b", "JORDAN"),
        ):
            response = lounge_control_client.post(
                "/internal/v1/matches",
                json={
                    "candidate_id": candidate_id,
                    "stream_id": stream_id,
                    "track_id": "track-01",
                    "status": "stable_match",
                    "confidence": 0.95,
                    "matched_at": "2026-10-07T12:00:00Z",
                },
                headers={"X-Internal-Token": "test-internal-token"},
            )
            assert response.status_code == 200
            assert response.json()["status"] == "delivered"
            recipient = phone_a if stream_id == "stream-a" else phone_b
            cue = recipient.receive_json()["cue"]
            assert display_name in cue["headline"]
            assert "guest_ref" not in cue

    assert device_manager.connected_count() == 0


@pytest.mark.parametrize("match_status", ["unconfirmed", "no_match"])
def test_non_stable_match_sends_clear_without_guest_profile(
    lounge_control_client,
    match_status,
):
    from apps_lounge_control import cohort_manager

    cohort_manager.admit_candidate(
        candidate_id="cand-hidden-profile",
        guest_ref="guest-alex-101",
        display_name="Alex",
        room_number="401",
        allergies=["Peanut allergy"],
        preferences=["Sparkling water"],
        expires_at="2099-01-01T00:00:00Z",
    )
    payload = {
        "candidate_id": "cand-hidden-profile",
        "stream_id": "stream-uncertain",
        "track_id": "track-01",
        "status": match_status,
        "confidence": 0.4,
        "matched_at": "2026-10-07T12:00:00Z",
    }

    with lounge_control_client.websocket_connect(
        "/v1/devices/phone-uncertain/stream?token=test-secret-token"
    ) as phone:
        assert phone.receive_json()["type"] == "session_ack"
        phone.send_json({
            "type": "frame_meta",
            "stream_id": "stream-uncertain",
            "sequence": 1,
            "captured_at": "2026-10-07T12:00:00Z",
        })
        phone.send_json({"type": "ping"})
        assert phone.receive_json()["type"] == "pong"

        response = lounge_control_client.post(
            "/internal/v1/matches",
            json=payload,
            headers={"X-Internal-Token": "test-internal-token"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "suppressed"
        clear = phone.receive_json()
        assert clear["type"] == "clear"
        assert clear["cue"] is None
        assert "Alex" not in str(clear)
        assert "Peanut allergy" not in str(clear)


def test_device_websocket_authenticated_and_frame_exchange(lounge_control_client):
    """Test authenticated WebSocket receives session_ack, sends frame, handles disconnect."""
    valid_token = "test-secret-token"

    with patch("apps_lounge_control.http_client") as mock_client:
        mock_post = AsyncMock()
        mock_post.status_code = 202
        mock_client.post = AsyncMock(return_value=mock_post)

        with lounge_control_client.websocket_connect(
            f"/v1/devices/device-test-1/stream?token={valid_token}"
        ) as ws:
            # 1. Initial session ack received
            ack = ws.receive_json()
            assert ack["type"] == "session_ack"
            assert ack["status"] == "authenticated"

            # 2. Send frame metadata text message
            meta = {
                "type": "frame_meta",
                "stream_id": "stream-glasses-01",
                "sequence": 1,
                "captured_at": "2026-10-07T12:00:00Z",
            }
            ws.send_json(meta)

            # 3. Send raw binary JPEG frame
            ws.send_bytes(SYNTHETIC_JPEG_BYTES)

            # 4. Ping/pong
            ws.send_json({"type": "ping"})
            pong = ws.receive_json()
            assert pong["type"] == "pong"


def test_match_callback_generates_emoji_cue(lounge_control_client):
    """Test match callback formats glanceable cue (🟢 ✅ ALEX / 🔴 ⚠️ PEANUT ALLERGY)."""
    from apps_lounge_control import cohort_manager, device_manager

    candidate_id = "cand-test-alex"
    stream_id = "stream-glasses-01"

    # Pre-populate active cohort
    cohort_manager.admit_candidate(
        candidate_id=candidate_id,
        guest_ref="guest-alex-101",
        display_name="Alex",
        room_number="401",
        allergies=["Peanut allergy"],
        preferences=["Sparkling water"],
        expires_at="2099-01-01T00:00:00Z",
    )

    # Post match event
    match_payload = {
        "candidate_id": candidate_id,
        "stream_id": stream_id,
        "track_id": "track-01",
        "status": "stable_match",
        "confidence": 0.95,
        "matched_at": "2026-10-07T12:00:00Z",
    }

    # If device not connected, returns status device_not_connected
    resp = lounge_control_client.post(
        "/internal/v1/matches",
        json=match_payload,
        headers={"X-Internal-Token": "test-internal-token"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "device_not_connected"
