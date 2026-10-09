"""Tests for tap-simulator and frame-replay scripts."""

import importlib.util
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Import simulator helpers
from fixtures.synthetic_data import (
    SYNTHETIC_FACE_JPEG_BYTES,
    SYNTHETIC_JPEG_BYTES,
    ensure_fixture_frame,
)


def test_ensure_synthetic_fixture(tmp_path):
    """Verify synthetic fixture file exists and is valid JPEG."""
    path = ensure_fixture_frame(tmp_path / "synthetic_frame.jpg")
    assert path.exists()
    content = path.read_bytes()
    assert len(content) > 0
    assert content[0] == 0xFF and content[1] == 0xD8
    assert content[-2] == 0xFF and content[-1] == 0xD9


@pytest.mark.asyncio
async def test_tap_simulator_send_event():
    """Test tap simulator sending an event via httpx mock."""
    path = REPO_ROOT / "apps" / "tap-simulator" / "main.py"
    spec = importlib.util.spec_from_file_location("tap_simulator_test_module", path)
    tap_main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tap_main)

    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"action": "admitted"}
    mock_client.post.return_value = mock_resp

    success = await tap_main.send_tap_event(
        client=mock_client,
        target_url="http://test/v1/lounge/taps",
        reader_id="reader-1",
        guest_ref="guest-alex-101",
        event_type="entry",
    )
    assert success is True
    mock_client.post.assert_called_once()
    args, kwargs = mock_client.post.call_args
    assert "json" in kwargs
    assert kwargs["json"]["guest_ref"] == "guest-alex-101"
    assert kwargs["json"]["event_type"] == "entry"


@pytest.mark.asyncio
async def test_frame_replay_load_fixture():
    """Test frame replay fixture loading helper."""
    path = REPO_ROOT / "apps" / "frame-replay" / "main.py"
    spec = importlib.util.spec_from_file_location("frame_replay_test_module", path)
    replay_main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(replay_main)

    fixture_bytes = replay_main.load_fixture(None)
    assert len(fixture_bytes) > 0
    assert fixture_bytes[0] == 0xFF and fixture_bytes[1] == 0xD8
    assert fixture_bytes == SYNTHETIC_FACE_JPEG_BYTES
