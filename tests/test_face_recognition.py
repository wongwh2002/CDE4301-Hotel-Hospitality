"""Focused unit checks for transient matching without model weights or real faces."""

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from contracts.models import MatchEvent


WORKER_PATH = Path(__file__).resolve().parent.parent / "apps" / "face-worker" / "worker.py"


class FakeFaceEngine:
    def create_template(self, photo_bytes):
        return photo_bytes.decode("ascii")

    def cosine_similarity(self, query, reference):
        return 0.9 if query == reference else 0.1


def load_worker_module():
    spec = importlib.util.spec_from_file_location("face_recognition_worker_test", WORKER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def detection(embedding="alex"):
    return SimpleNamespace(bbox=(10.0, 10.0, 30.0, 30.0), embedding=embedding)


def test_match_requires_three_stable_observations_then_clears():
    worker = load_worker_module()
    worker.set_face_engine(FakeFaceEngine())
    worker.enroll_candidate("cand-alex", b"alex", "2099-01-01T00:00:00Z")

    assert worker._process_frame("device-1", "stream-1", [detection()]) == []
    assert worker._process_frame("device-1", "stream-1", [detection()]) == []
    match = worker._process_frame("device-1", "stream-1", [detection()])
    assert len(match) == 1
    assert match[0]["status"] == "stable_match"
    assert match[0]["candidate_id"] == "cand-alex"

    assert worker._process_frame("device-1", "stream-1", []) == []
    assert worker._process_frame("device-1", "stream-1", []) == []
    cleared = worker._process_frame("device-1", "stream-1", [])
    assert len(cleared) == 1
    assert cleared[0]["status"] == "no_match"
    assert cleared[0]["candidate_id"] is None


def test_match_contract_requires_candidate_only_for_stable_match():
    event = MatchEvent(
        stream_id="stream-1",
        track_id="track-1",
        status="no_match",
        matched_at="2026-10-09T00:00:00Z",
    )
    assert event.candidate_id is None

    with pytest.raises(ValueError, match="stable_match requires candidate_id"):
        MatchEvent(
            stream_id="stream-1",
            track_id="track-1",
            status="stable_match",
            matched_at="2026-10-09T00:00:00Z",
        )
