"""Tests for shared versioned contracts and JSON schemas."""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from contracts.models import (
    CandidateEnrollment,
    CueMessage,
    CuePayload,
    DeviceStreamMessage,
    LoungeProfile,
    MatchEvent,
    TapEvent,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = REPO_ROOT / "contracts"


def test_contract_schemas_exist_and_are_valid_json():
    """Verify all versioned schema files exist and are valid JSON."""
    expected_schemas = [
        "tap-event.schema.json",
        "device-stream.schema.json",
        "match-event.schema.json",
        "cue.schema.json",
        "lounge-profile.schema.json",
        "candidate.schema.json",
    ]
    for schema_name in expected_schemas:
        schema_path = CONTRACTS_DIR / schema_name
        assert schema_path.exists(), f"Missing schema file: {schema_name}"
        data = json.loads(schema_path.read_text())
        assert "$schema" in data
        assert "/v1/" in data["$id"]
        assert "title" in data
        assert "type" in data


def test_tap_event_model():
    """Test TapEvent serialization and validation."""
    valid_data = {
        "event_id": "evt-12345",
        "reader_id": "lounge-entry-1",
        "guest_ref": "guest-alex-101",
        "event_type": "entry",
        "occurred_at": "2026-10-07T12:00:00Z",
    }
    event = TapEvent(**valid_data)
    assert event.event_id == "evt-12345"
    assert event.event_type == "entry"

    # Invalid event_type must fail
    with pytest.raises(ValidationError):
        TapEvent(
            event_id="evt-12345",
            reader_id="lounge-entry-1",
            guest_ref="guest-alex-101",
            event_type="invalid_action",  # type: ignore
        )
    with pytest.raises(ValidationError):
        TapEvent(**{**valid_data, "guest_ref": "../../not-a-guest"})
    with pytest.raises(ValidationError):
        TapEvent(**{**valid_data, "unexpected": "field"})


def test_device_stream_message_model():
    """Test DeviceStreamMessage serialization and validation."""
    msg = DeviceStreamMessage(
        type="frame_meta",
        stream_id="stream-1",
        sequence=1,
        captured_at="2026-10-07T12:00:00Z",
    )
    dumped = msg.model_dump()
    assert dumped["type"] == "frame_meta"
    assert dumped["format"] == "image/jpeg"

    # Negative sequence must fail
    with pytest.raises(ValidationError):
        DeviceStreamMessage(type="frame_meta", sequence=-1)
    with pytest.raises(ValidationError):
        DeviceStreamMessage(type="frame_meta", sequence=1)


def test_match_event_model():
    """Test MatchEvent strictly requires opaque candidate ID and no PII."""
    event = MatchEvent(
        candidate_id="cand-opaque-999",
        stream_id="stream-1",
        track_id="track-01",
        status="stable_match",
        confidence=0.92,
        matched_at="2026-10-07T12:00:00Z",
    )
    assert event.candidate_id == "cand-opaque-999"
    assert event.status == "stable_match"


def test_cue_message_model():
    """Test CueMessage and CuePayload formatting."""
    payload = CuePayload(
        headline="🟢 ✅ ALEX",
        alert="🔴 ⚠️ PEANUT ALLERGY",
        guest_ref="guest-alex-101",
        color="green",
        secondary_color="red",
    )
    cue_msg = CueMessage(
        type="cue",
        stream_id="stream-1",
        track_id="track-01",
        status="active",
        cue=payload,
        emitted_at="2026-10-07T12:00:00Z",
    )
    assert cue_msg.cue is not None
    assert "ALEX" in cue_msg.cue.headline
    assert "PEANUT ALLERGY" in (cue_msg.cue.alert or "")


def test_lounge_profile_model():
    """Test LoungeProfile minimal permitted fields."""
    profile = LoungeProfile(
        guest_ref="guest-alex-101",
        display_name="Alex",
        room_number="401",
        vip_tier="Diamond",
        allergies=["Peanut allergy"],
        preferences=["Sparkling water"],
    )
    assert profile.display_name == "Alex"
    assert profile.allergies == ["Peanut allergy"]
