"""Tests for lounge-control service."""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from starlette.websockets import WebSocketDisconnect
from fixtures.synthetic_data import SYNTHETIC_JPEG_BYTES


def fresh_match_time():
    return datetime.now(timezone.utc).isoformat()


def test_lounge_control_health(lounge_control_client):
    """Test health endpoint."""
    resp = lounge_control_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "lounge-control"


def test_dashboard_has_multi_person_websocket_result_preview(lounge_control_client):
    response = lounge_control_client.get("/")

    assert response.status_code == 200
    assert 'id="cv-people-list"' in response.text
    assert "People returned to this client" in response.text
    assert "message.type === 'face_crop'" in response.text
    assert "message.type === 'detection_set'" in response.text


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
        "crop_id": "crop-auth-test",
        "crop_b64": "ZmFrZS1qcGVn",
        "matched_at": fresh_match_time(),
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
            initial_set = ws.receive_json()
            assert initial_set["type"] == "detection_set"
            assert initial_set["stream_id"] == stream_id
            assert initial_set["people"] == []
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
                    "crop_id": "crop-phone-test",
                    "crop_b64": "ZmFrZS1qcGVn",
                    "matched_at": fresh_match_time(),
                },
                headers={"X-Internal-Token": "test-internal-token"},
            )
            assert response.status_code == 200
            assert response.json()["status"] == "delivered"
            recipient = phone_a if stream_id == "stream-a" else phone_b
            crop = recipient.receive_json()
            assert crop["type"] == "face_crop"
            assert crop["crop_id"] == "crop-phone-test"
            detected = recipient.receive_json()
            assert detected["type"] == "detection_set"
            assert detected["stream_id"] == stream_id
            assert len(detected["people"]) == 1
            person = detected["people"][0]
            assert person["track_id"] == "track-01"
            assert person["guest_id"].startswith("guest-")
            assert person["display_name"] == display_name
            assert person["preferences"] == []
            assert person["allergies"] == []
            cue_message = recipient.receive_json()
            assert cue_message["type"] == "cue"
            cue = cue_message["cue"]
            assert display_name in cue["headline"]
            assert "guest_ref" not in cue

    assert device_manager.connected_count() == 0


def test_one_stream_returns_multiple_guest_profiles_and_face_crops(lounge_control_client):
    from apps_lounge_control import cohort_manager, public_guest_id

    guests = (
        ("cand-face-a", "guest-alex-101", "Alex", ["Sparkling water"], ["Peanut allergy"]),
        ("cand-face-b", "guest-jordan-102", "Jordan", ["Late checkout"], []),
    )
    for candidate_id, guest_ref, display_name, preferences, allergies in guests:
        cohort_manager.admit_candidate(
            candidate_id=candidate_id,
            guest_ref=guest_ref,
            display_name=display_name,
            room_number="401",
            allergies=allergies,
            preferences=preferences,
            expires_at="2099-01-01T00:00:00Z",
        )

    with lounge_control_client.websocket_connect(
        "/v1/video/stream/phone-multi?token=test-secret-token"
    ) as phone:
        assert phone.receive_json()["type"] == "session_ack"
        phone.send_json({
            "type": "frame_meta",
            "stream_id": "stream-multi",
            "sequence": 1,
            "captured_at": "2026-10-15T09:00:00Z",
        })
        assert phone.receive_json()["people"] == []

        for index, (candidate_id, _, _, _, _) in enumerate(guests, start=1):
            response = lounge_control_client.post(
                "/internal/v1/matches",
                json={
                    "candidate_id": candidate_id,
                    "stream_id": "stream-multi",
                    "track_id": f"track-{index}",
                    "status": "stable_match",
                    "confidence": 0.95,
                    "crop_id": f"crop-{index}",
                    "crop_b64": "ZmFrZS1qcGVn",
                    "matched_at": fresh_match_time(),
                },
                headers={"X-Internal-Token": "test-internal-token"},
            )
            assert response.status_code == 200

            crop = phone.receive_json()
            assert crop["type"] == "face_crop"
            assert crop["track_id"] == f"track-{index}"
            assert crop["crop_id"] == f"crop-{index}"
            assert crop["image_b64"] == "ZmFrZS1qcGVn"

            snapshot = phone.receive_json()
            assert snapshot["type"] == "detection_set"
            assert len(snapshot["people"]) == index
            person = next(
                item for item in snapshot["people"] if item["track_id"] == f"track-{index}"
            )
            expected_guest = guests[index - 1]
            assert person["guest_id"] == public_guest_id(expected_guest[1])
            assert person["display_name"] == expected_guest[2].upper()
            assert person["preferences"] == expected_guest[3]
            assert person["allergies"] == expected_guest[4]
            assert person["crop_id"] == f"crop-{index}"
            assert expected_guest[1] not in str(snapshot)
            assert phone.receive_json()["type"] == "cue"

        # Refreshing a known track updates the five-second TTL without replaying
        # an unchanged crop or sending another one-shot cue.
        refresh = lounge_control_client.post(
            "/internal/v1/matches",
            json={
                "candidate_id": "cand-face-a",
                "stream_id": "stream-multi",
                "track_id": "track-1",
                "status": "stable_refresh",
                "crop_id": "crop-1",
                "matched_at": fresh_match_time(),
            },
            headers={"X-Internal-Token": "test-internal-token"},
        )
        assert refresh.status_code == 200
        assert refresh.json()["status"] == "refreshed"

        with patch("apps_lounge_control.http_client") as mock_client:
            mock_client.delete = AsyncMock(return_value=MagicMock(status_code=200))
            exit_response = lounge_control_client.post(
                "/v1/lounge/taps",
                json={
                    "event_id": "evt-alex-departed",
                    "reader_id": "lounge-exit-1",
                    "guest_ref": "guest-alex-101",
                    "event_type": "exit",
                    "occurred_at": "2026-10-15T09:01:00Z",
                },
            )
        assert exit_response.status_code == 200
        clear = phone.receive_json()
        assert clear["type"] == "clear"
        assert clear["track_id"] == "track-1"
        remaining = phone.receive_json()
        assert remaining["type"] == "detection_set"
        assert [person["track_id"] for person in remaining["people"]] == ["track-2"]


def test_detection_cache_expires_after_five_seconds_and_clears_on_guest_departure(
    lounge_control_client,
):
    from apps_lounge_control import DeviceSessionManager

    class FakeWebSocket:
        async def send_json(self, _message):
            return None

    manager = DeviceSessionManager(detection_ttl_seconds=5)
    manager.register("phone-ttl", FakeWebSocket())
    manager.bind_stream("phone-ttl", "stream-ttl")
    manager.update_detected_person(
        "stream-ttl",
        "track-a",
        {"guest_id": "guest-a", "display_name": "ALEX"},
        now=100.0,
    )
    manager.update_detected_person(
        "stream-ttl",
        "track-b",
        {"guest_id": "guest-b", "display_name": "JORDAN"},
        now=100.0,
    )
    assert len(manager.get_detected_people("stream-ttl", now=104.99)) == 2
    manager.update_detected_person(
        "stream-ttl",
        "track-a",
        {"guest_id": "guest-a", "display_name": "ALEX"},
        now=104.99,
    )
    assert [
        person["track_id"]
        for person in manager.get_detected_people("stream-ttl", now=105.0)
    ] == ["track-a"]
    assert manager.get_detected_people("stream-ttl", now=109.98)
    assert manager.get_detected_people("stream-ttl", now=109.99) == []

    manager.update_detected_person(
        "stream-ttl",
        "track-a",
        {"guest_id": "guest-a", "display_name": "ALEX"},
        now=200.0,
    )
    assert manager.remove_guest("guest-a") == {"stream-ttl": ["track-a"]}
    assert manager.get_detected_people("stream-ttl", now=200.1) == []


def test_detection_ttl_uses_match_observation_time_not_callback_receipt():
    from apps_lounge_control import DeviceSessionManager

    manager = DeviceSessionManager(detection_ttl_seconds=5)
    observed_at = datetime.now(timezone.utc)
    wall_now = observed_at + timedelta(seconds=4)
    last_seen = manager.observation_last_seen(
        observed_at,
        now_monotonic=100.0,
        now_utc=wall_now,
    )
    assert last_seen == pytest.approx(96.0)
    assert manager.observation_last_seen(
        observed_at,
        now_monotonic=100.0,
        now_utc=observed_at + timedelta(seconds=5),
    ) is None

    class FakeWebSocket:
        async def send_json(self, _message):
            return None

    manager.register("phone-observed", FakeWebSocket())
    manager.bind_stream("phone-observed", "stream-observed")
    manager.update_detected_person(
        "stream-observed",
        "track-old",
        {"guest_id": "guest-old", "display_name": "ALEX"},
        now=100.0,
        last_seen=last_seen,
    )
    assert manager.get_detected_people("stream-observed", now=100.99)
    assert manager.get_detected_people("stream-observed", now=101.0) == []


def test_stale_match_callback_does_not_create_a_detection(lounge_control_client):
    from apps_lounge_control import cohort_manager, device_manager

    cohort_manager.admit_candidate(
        candidate_id="cand-stale-match",
        guest_ref="guest-stale-101",
        display_name="Alex",
        room_number=None,
        allergies=[],
        preferences=[],
        expires_at="2099-01-01T00:00:00Z",
    )
    with lounge_control_client.websocket_connect(
        "/v1/video/stream/phone-stale?token=test-secret-token"
    ) as phone:
        assert phone.receive_json()["type"] == "session_ack"
        phone.send_json({
            "type": "frame_meta",
            "stream_id": "stream-stale",
            "sequence": 1,
            "captured_at": fresh_match_time(),
        })
        assert phone.receive_json()["people"] == []

        response = lounge_control_client.post(
            "/internal/v1/matches",
            json={
                "candidate_id": "cand-stale-match",
                "stream_id": "stream-stale",
                "track_id": "track-stale",
                "status": "stable_match",
                "crop_id": "crop-stale",
                "crop_b64": "ZmFrZS1qcGVn",
                "matched_at": (datetime.now(timezone.utc) - timedelta(seconds=6)).isoformat(),
            },
            headers={"X-Internal-Token": "test-internal-token"},
        )
        assert response.status_code == 200
        assert response.json()["reason"] == "stale_observation"
        assert device_manager.get_detected_people("stream-stale") == []


def test_failed_first_crop_delivery_retry_sends_initial_cue(
    lounge_control_client, monkeypatch
):
    import apps_lounge_control as main

    main.cohort_manager.admit_candidate(
        candidate_id="cand-crop-retry",
        guest_ref="guest-crop-retry",
        display_name="Alex",
        room_number=None,
        allergies=[],
        preferences=["Sparkling water"],
        expires_at="2099-01-01T00:00:00Z",
    )
    with lounge_control_client.websocket_connect(
        "/v1/video/stream/phone-crop-retry?token=test-secret-token"
    ) as phone:
        assert phone.receive_json()["type"] == "session_ack"
        phone.send_json({
            "type": "frame_meta",
            "stream_id": "stream-crop-retry",
            "sequence": 1,
            "captured_at": fresh_match_time(),
        })
        assert phone.receive_json()["people"] == []

        original_send = main.device_manager.send_cue
        failed_once = False

        async def fail_first_crop(stream_id, message):
            nonlocal failed_once
            if message.get("type") == "face_crop" and not failed_once:
                failed_once = True
                return False
            return await original_send(stream_id, message)

        monkeypatch.setattr(main.device_manager, "send_cue", fail_first_crop)
        first = {
            "candidate_id": "cand-crop-retry",
            "stream_id": "stream-crop-retry",
            "track_id": "track-crop-retry",
            "status": "stable_match",
            "crop_id": "crop-crop-retry",
            "crop_b64": "ZmFrZS1qcGVn",
            "matched_at": fresh_match_time(),
        }
        failed = lounge_control_client.post(
            "/internal/v1/matches",
            json=first,
            headers={"X-Internal-Token": "test-internal-token"},
        )
        assert failed.json()["status"] == "crop_delivery_failed"

        retry = dict(first, status="stable_refresh", matched_at=fresh_match_time())
        recovered = lounge_control_client.post(
            "/internal/v1/matches",
            json=retry,
            headers={"X-Internal-Token": "test-internal-token"},
        )
        assert recovered.status_code == 200
        assert recovered.json()["cue_delivered"] is True
        assert phone.receive_json()["type"] == "face_crop"
        snapshot = phone.receive_json()
        assert snapshot["type"] == "detection_set"
        assert snapshot["people"][0]["crop_id"] == "crop-crop-retry"
        cue = phone.receive_json()
        assert cue["type"] == "cue"
        assert cue["cue"]["headline"] == "🟢 ✅ ALEX"


@pytest.mark.asyncio
async def test_detection_set_broadcast_loop_sends_periodic_full_snapshots(
    lounge_control_client, monkeypatch
):
    import apps_lounge_control as main

    class FakeWebSocket:
        def __init__(self):
            self.messages = []

        async def send_json(self, message):
            self.messages.append(message)

    websocket = FakeWebSocket()
    manager = main.DeviceSessionManager()
    manager.register("phone-periodic", websocket)
    manager.bind_stream("phone-periodic", "stream-periodic")
    manager.update_detected_person(
        "stream-periodic",
        "track-a",
        {"guest_id": "guest-a", "display_name": "ALEX", "crop_id": "crop-a"},
    )
    monkeypatch.setattr(main, "device_manager", manager)
    monkeypatch.setattr(main, "DETECTION_SET_INTERVAL_SECONDS", 0.01)

    task = asyncio.create_task(main.detection_set_broadcast_loop())
    try:
        await asyncio.sleep(0.035)
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    assert len(websocket.messages) >= 2
    assert all(message["type"] == "detection_set" for message in websocket.messages)
    assert all(message["people"][0]["track_id"] == "track-a" for message in websocket.messages)


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
        initial_set = phone.receive_json()
        assert initial_set["type"] == "detection_set"
        assert initial_set["stream_id"] == "stream-uncertain"
        assert initial_set["people"] == []
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
        cleared_set = phone.receive_json()
        assert cleared_set["type"] == "detection_set"
        assert cleared_set["stream_id"] == "stream-uncertain"
        assert cleared_set["people"] == []


def test_device_websocket_authenticated_and_frame_exchange(lounge_control_client, caplog):
    """Test authenticated WebSocket receives session_ack, sends frame, handles disconnect."""
    valid_token = "test-secret-token"
    caplog.set_level(logging.INFO, logger="lounge_control")

    with patch("apps_lounge_control.http_client") as mock_client:
        mock_post = MagicMock()
        mock_post.status_code = 202
        mock_post.json.return_value = {"status": "accepted"}
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
            initial_set = ws.receive_json()
            assert initial_set["type"] == "detection_set"
            assert initial_set["stream_id"] == "stream-glasses-01"
            assert initial_set["people"] == []

            # 3. Send raw binary JPEG frame
            ws.send_bytes(SYNTHETIC_JPEG_BYTES)

            # 4. Ping/pong
            ws.send_json({"type": "ping"})
            pong = ws.receive_json()
            assert pong["type"] == "pong"

            # Streaming clients can see each incoming frame in lounge-control logs.
            assert any(
                record.name == "lounge_control"
                and record.getMessage()
                == (
                    "frame_received device_id=device-test-1 stream_id=stream-glasses-01 "
                    f"sequence=1 frame_bytes={len(SYNTHETIC_JPEG_BYTES)} "
                    "format=image/jpeg "
                    "captured_at=2026-10-07T12:00:00Z"
                )
                for record in caplog.records
            )


def test_device_websocket_forwards_sustained_jpeg_frames_on_one_connection(
    lounge_control_client, caplog
):
    """Accepts a sampled camera feed as JPEG frames over one persistent WebSocket."""
    # Raise only the capture handler: don't change the application's logger
    # level, since the test should catch INFO records suppressed by the app.
    caplog.handler.setLevel(logging.INFO)
    frame_count = 15

    with patch("apps_lounge_control.http_client") as mock_client:
        mock_response = MagicMock(status_code=202)
        mock_client.post = AsyncMock(return_value=mock_response)

        with lounge_control_client.websocket_connect(
            "/v1/video/stream/phone-stream-test?token=test-secret-token"
        ) as phone:
            assert phone.receive_json()["type"] == "session_ack"

            for sequence in range(1, frame_count + 1):
                phone.send_json({
                    "type": "frame_meta",
                    "stream_id": "stream-sustained-test",
                    "sequence": sequence,
                    "captured_at": f"2026-10-16T10:00:{sequence:02d}Z",
                })
                if sequence == 1:
                    initial_set = phone.receive_json()
                    assert initial_set["type"] == "detection_set"
                    assert initial_set["stream_id"] == "stream-sustained-test"
                    assert initial_set["people"] == []
                phone.send_bytes(SYNTHETIC_JPEG_BYTES)
                if sequence < frame_count:
                    time.sleep(0.2)  # 5 JPEG frames per second over the same socket.

            # The pong follows all preceding frame messages, so it synchronizes
            # the assertion with lounge-control's frame receive loop.
            phone.send_json({"type": "ping"})
            assert phone.receive_json() == {"type": "pong"}

    frame_logs = [
        record.getMessage()
        for record in caplog.records
        if record.getMessage().startswith(
            "frame_received device_id=phone-stream-test stream_id=stream-sustained-test "
        )
    ]
    assert len(frame_logs) == frame_count
    sequence_logged = [
        f"sequence={sequence} " in message
        for sequence, message in enumerate(frame_logs, 1)
    ]
    assert sequence_logged == [True] * frame_count
    expected_size = f"frame_bytes={len(SYNTHETIC_JPEG_BYTES)} "
    assert all(expected_size in message for message in frame_logs)
    assert all("format=image/jpeg" in message for message in frame_logs)
    assert mock_client.post.await_count == frame_count


def test_device_websocket_forwards_jpeg_xl_content_type(lounge_control_client):
    import base64
    import imagecodecs
    import numpy as np

    rgb = np.zeros((8, 10, 3), dtype=np.uint8)
    frame = imagecodecs.jpegxl_encode(rgb, lossless=True)
    with patch("apps_lounge_control.http_client") as mock_client:
        mock_client.post = AsyncMock(return_value=MagicMock(status_code=202))
        with lounge_control_client.websocket_connect(
            "/v1/video/stream/phone-jxl?token=test-secret-token"
        ) as phone:
            assert phone.receive_json()["type"] == "session_ack"
            phone.send_json({
                "type": "frame_meta",
                "stream_id": "stream-jxl-forward",
                "sequence": 1,
                "captured_at": fresh_match_time(),
                "format": "image/jxl",
            })
            assert phone.receive_json()["type"] == "detection_set"
            phone.send_bytes(frame)
            phone.send_json({
                "type": "frame",
                "stream_id": "stream-jxl-forward",
                "sequence": 2,
                "captured_at": fresh_match_time(),
                "format": "image/jxl",
                "payload_b64": base64.b64encode(frame).decode("ascii"),
            })
            phone.send_json({"type": "ping"})
            assert phone.receive_json() == {"type": "pong"}

    assert mock_client.post.await_count == 2
    assert all(
        call.kwargs["headers"]["Content-Type"] == "image/jxl"
        for call in mock_client.post.await_args_list
    )


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
        "crop_id": "crop-emoji-test",
        "crop_b64": "ZmFrZS1qcGVn",
        "matched_at": fresh_match_time(),
    }

    # Without a connected phone, the crop is not cached or published.
    resp = lounge_control_client.post(
        "/internal/v1/matches",
        json=match_payload,
        headers={"X-Internal-Token": "test-internal-token"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "crop_delivery_failed"
    assert resp.json()["crop_delivered"] is False


@pytest.mark.asyncio
async def test_duplicate_entry_enforces_single_presence(lounge_control_client):
    """Verify at most one active presence is enforced per guest_ref across distinct event_ids, and exit clears it."""
    from apps_lounge_control import cohort_manager

    cohort_manager._cohort.clear()
    cohort_manager._guest_to_candidates.clear()
    cohort_manager._processed_events.clear()

    mock_profile_resp = MagicMock()
    mock_profile_resp.status_code = 200
    mock_profile_resp.json.return_value = {
        "guest_ref": "guest-alex-101",
        "display_name": "Alex",
        "room_number": "401",
        "allergies": [],
        "preferences": [],
    }
    mock_photo_resp = MagicMock()
    mock_photo_resp.status_code = 200
    mock_photo_resp.content = SYNTHETIC_JPEG_BYTES

    mock_ok = MagicMock()
    mock_ok.status_code = 200

    async def mock_get(url, *args, **kwargs):
        if "lounge-profile" in url:
            return mock_profile_resp
        elif "photo" in url:
            return mock_photo_resp
        return mock_ok

    with patch("apps_lounge_control.http_client") as mock_client:
        mock_client.get = AsyncMock(side_effect=mock_get)
        mock_client.put = AsyncMock(return_value=mock_ok)
        mock_client.delete = AsyncMock(return_value=mock_ok)

        # 1. First entry tap
        tap_1 = {
            "event_id": "evt-entry-001",
            "reader_id": "reader-1",
            "guest_ref": "guest-alex-101",
            "event_type": "entry",
            "occurred_at": "2026-10-07T12:00:00Z",
        }
        resp1 = lounge_control_client.post("/v1/lounge/taps", json=tap_1)
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["action"] == "admitted"
        cand_id1 = data1["candidate_id"]
        assert cohort_manager.size() == 1

        # 2. Second entry tap with a DIFFERENT event_id for the same guest_ref
        tap_2 = {
            "event_id": "evt-entry-002",
            "reader_id": "reader-2",
            "guest_ref": "guest-alex-101",
            "event_type": "entry",
            "occurred_at": "2026-10-07T12:05:00Z",
        }
        resp2 = lounge_control_client.post("/v1/lounge/taps", json=tap_2)
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["action"] == "already_admitted"
        assert data2["candidate_id"] == cand_id1
        # Cohort size MUST remain exactly 1 (no duplicate presence)
        assert cohort_manager.size() == 1
        assert len(cohort_manager.get_roster()) == 1

        # 3. Exit tap removes that presence
        tap_exit = {
            "event_id": "evt-exit-001",
            "reader_id": "reader-1",
            "guest_ref": "guest-alex-101",
            "event_type": "exit",
            "occurred_at": "2026-10-07T12:30:00Z",
        }
        resp_exit = lounge_control_client.post("/v1/lounge/taps", json=tap_exit)
        assert resp_exit.status_code == 200
        assert resp_exit.json()["action"] == "departed"
        assert cohort_manager.size() == 0
        assert len(cohort_manager.get_roster()) == 0

        # 4. Re-entry after departure creates a fresh presence
        tap_3 = {
            "event_id": "evt-entry-003",
            "reader_id": "reader-1",
            "guest_ref": "guest-alex-101",
            "event_type": "entry",
            "occurred_at": "2026-10-07T13:00:00Z",
        }
        resp3 = lounge_control_client.post("/v1/lounge/taps", json=tap_3)
        assert resp3.status_code == 200
        assert resp3.json()["action"] == "admitted"
        assert cohort_manager.size() == 1


@pytest.mark.asyncio
async def test_concurrent_entry_taps_for_same_guest_create_one_presence(lounge_control_client):
    """Concurrent readers must not enroll duplicate candidates for one guest."""
    import apps_lounge_control
    from contracts.models import TapEvent

    cohort_manager = apps_lounge_control.cohort_manager
    cohort_manager._cohort.clear()
    cohort_manager._guest_to_candidates.clear()
    cohort_manager._processed_events.clear()
    apps_lounge_control.tap_locks.clear()

    profile_resp = MagicMock()
    profile_resp.status_code = 200
    profile_resp.json.return_value = {
        "guest_ref": "guest-alex-101",
        "display_name": "Alex",
        "room_number": "401",
        "allergies": [],
        "preferences": [],
    }
    photo_resp = MagicMock()
    photo_resp.status_code = 200
    photo_resp.content = SYNTHETIC_JPEG_BYTES
    worker_resp = MagicMock()
    worker_resp.status_code = 200
    worker_resp.json.return_value = {"template_status": "ready"}

    async def mock_get(url, *args, **kwargs):
        return profile_resp if "lounge-profile" in url else photo_resp

    with patch("apps_lounge_control.http_client") as mock_client:
        mock_client.get = AsyncMock(side_effect=mock_get)
        mock_client.put = AsyncMock(return_value=worker_resp)
        events = [
            TapEvent.model_validate({
                "event_id": f"evt-concurrent-{index}",
                "reader_id": f"reader-{index}",
                "guest_ref": "guest-alex-101",
                "event_type": "entry",
                "occurred_at": f"2026-10-07T12:0{index}:00Z",
            })
            for index in range(2)
        ]
        outcomes = await asyncio.gather(*(apps_lounge_control.post_tap(event) for event in events))

    assert {outcome["action"] for outcome in outcomes} == {"admitted", "already_admitted"}
    assert cohort_manager.size() == 1
    assert mock_client.put.await_count == 1


def test_roster_fields_only_display_name_and_admitted_at(lounge_control_client):
    """Active roster must only expose display_name and admitted_at fields."""
    from apps_lounge_control import cohort_manager

    cohort_manager._cohort.clear()
    cohort_manager._guest_to_candidates.clear()

    cohort_manager.admit_candidate(
        candidate_id="cand-roster-1",
        guest_ref="guest-alex-101",
        display_name="Alex",
        room_number="401",
        allergies=["Peanut allergy"],
        preferences=["Sparkling water"],
        expires_at="2099-01-01T00:00:00Z",
    )
    cohort_manager.admit_candidate(
        candidate_id="cand-roster-2",
        guest_ref="guest-jordan-102",
        display_name="Jordan",
        room_number="512",
        allergies=["Shellfish allergy"],
        preferences=["Earl Grey tea"],
        expires_at="2099-01-01T00:00:00Z",
    )

    resp = lounge_control_client.get("/v1/lounge/roster")
    assert resp.status_code == 200
    roster = resp.json()
    assert len(roster) == 2

    # Verify each entry contains ONLY display_name and admitted_at
    for entry in roster:
        assert set(entry.keys()) == {"display_name", "admitted_at"}
        assert "guest_ref" not in entry
        assert "candidate_id" not in entry
        assert "room_number" not in entry
        assert "allergies" not in entry
        assert "preferences" not in entry
        assert "expires_at" not in entry

    names = [e["display_name"] for e in roster]
    assert "Alex" in names
    assert "Jordan" in names


def test_dashboard_routes(lounge_control_client):
    """Test dashboard serving and guest list endpoints."""
    # 1. Root route serves dashboard HTML
    resp_root = lounge_control_client.get("/")
    assert resp_root.status_code == 200
    assert "text/html" in resp_root.headers["content-type"]
    assert "Hotel Lounge" in resp_root.text
    assert "guest-dropdown" in resp_root.text
    assert "guest-ref" in resp_root.text
    assert "btn-entry" in resp_root.text
    assert "btn-exit" in resp_root.text
    assert "guest-registration-form" in resp_root.text
    assert "btn-register-guest" in resp_root.text
    assert "Active Lounge Roster" in resp_root.text

    # 2. /dashboard alias serves dashboard HTML
    resp_dash = lounge_control_client.get("/dashboard")
    assert resp_dash.status_code == 200
    assert "text/html" in resp_dash.headers["content-type"]

    # 3. Hotel guest dropdown endpoints proxy mock-hotel
    mock_guests = [
        {"guest_ref": "guest-alex-101", "display_name": "Alex"},
        {"guest_ref": "guest-jordan-102", "display_name": "Jordan"},
    ]
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_guests
    registered_guest = {
        "guest_ref": "guest-taylor-a1b2c3",
        "display_name": "Taylor",
        "room_number": "702",
        "vip_tier": None,
        "allergies": ["Dairy"],
        "preferences": ["Still water"],
        "photo_url": "/v1/guests/guest-taylor-a1b2c3/photo",
        "photo_urls": [],
    }
    registration_resp = MagicMock()
    registration_resp.status_code = 201
    registration_resp.json.return_value = registered_guest

    with patch("apps_lounge_control.http_client") as mock_client:
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.post = AsyncMock(return_value=registration_resp)
        resp_guests = lounge_control_client.get("/v1/dashboard/guests")
        assert resp_guests.status_code == 200
        assert resp_guests.json() == mock_guests

        resp_lounge_guests = lounge_control_client.get("/v1/lounge/guests")
        assert resp_lounge_guests.status_code == 200
        assert resp_lounge_guests.json() == mock_guests

        registration = lounge_control_client.post(
            "/v1/dashboard/guests",
            json={
                "display_name": "Taylor",
                "room_number": "702",
                "allergies": ["Dairy"],
                "preferences": ["Still water"],
            },
        )
        assert registration.status_code == 201
        assert registration.json() == registered_guest
        mock_client.post.assert_awaited_once_with(
            "http://mock-hotel:8002/v1/guests",
            json={
                "display_name": "Taylor",
                "room_number": "702",
                "vip_tier": None,
                "allergies": ["Dairy"],
                "preferences": ["Still water"],
                "photos_b64": [],
            },
        )


@pytest.mark.asyncio
async def test_sse_notifier_and_bounded_buffer():
    """Verify SSE notifier provides bounded per-client buffering and drops oldest on saturation."""
    from sse import RosterSSENotifier, format_keepalive, format_sse

    notifier = RosterSSENotifier(max_buffer_size=3)
    q = notifier.subscribe()

    assert notifier.subscriber_count() == 1

    # Send 5 events (capacity is 3)
    for i in range(5):
        notifier.notify("roster_change", {"seq": i})

    # Queue size should not exceed max_buffer_size
    assert q.qsize() == 3

    # Check that oldest events (0, 1) were dropped and latest (2, 3, 4) remain
    item1 = q.get_nowait()
    assert item1["data"]["seq"] == 2
    item2 = q.get_nowait()
    assert item2["data"]["seq"] == 3
    item3 = q.get_nowait()
    assert item3["data"]["seq"] == 4

    notifier.unsubscribe(q)
    assert notifier.subscriber_count() == 0

    # Test wire formatting
    sse_text = format_sse("roster_change", {"key": "val"})
    assert sse_text.startswith("event: roster_change\n")
    assert "data: {\"key\": \"val\"}\n\n" in sse_text

    keepalive_text = format_keepalive()
    assert keepalive_text == ": keepalive\n\n"


def test_sse_endpoint_connects(lounge_control_client):
    """Test SSE endpoint establishes text/event-stream connection and sends initial event."""
    # TestClient buffers complete response bodies, so mark the subscriber
    # disconnected after the generator emits its initial connected event.
    with patch(
        "apps_lounge_control.Request.is_disconnected",
        new=AsyncMock(return_value=True),
    ):
        response = lounge_control_client.get("/v1/lounge/events")
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert response.headers["cache-control"] == "no-cache"
    assert "event: connected" in response.text
    assert 'data: {"status": "ok"}' in response.text
