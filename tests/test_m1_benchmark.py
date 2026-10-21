import hashlib
from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from compare_m1_benchmarks import compare_reports  # noqa: E402
from m1_benchmark import (  # noqa: E402
    load_frames,
    percentile,
    timing_summary,
    throughput_metrics,
)


def test_percentile_uses_nearest_rank_and_empty_is_none():
    assert percentile([9, 1, 5, 3], 50) == 3
    assert percentile([9, 1, 5, 3], 95) == 9
    assert percentile([], 50) is None


def test_timing_summary_reports_p50_p95_and_mean():
    assert timing_summary([1, 2, 3, 4]) == {
        "p50_ms": 2,
        "p95_ms": 4,
        "mean_ms": 2.5,
    }


def test_throughput_uses_processing_window_not_user_wait_timeout():
    rate, duration = throughput_metrics(
        processed_count=3,
        stream_started=100.0,
        send_finished=104.5,
        result_arrivals={1: 102.0, 5: 105.0, 10: 108.0},
    )

    assert rate == 0.375
    assert duration == 8.0


def test_load_frames_converts_png_to_jpeg_for_supported_stream_format():
    path = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_multi_face.png"

    frames, fingerprints = load_frames([path])

    assert frames[0].startswith(b"\xff\xd8")
    assert fingerprints[0] != hashlib.sha256(path.read_bytes()).hexdigest()


def test_compare_reports_requires_same_workload_and_measures_decision_agreement():
    workload = {
        "frame_count_requested": 2,
        "frame_interval_seconds": 0.5,
        "frame_sha256": ["same-input"],
        "reference_sha256": [],
    }
    first = {
        "schema": "m1-face-worker-benchmark/v1",
        "label": "docker",
        "runtime": {"requested_execution_provider": "cpu"},
        "workload": workload,
        "results": {
            "per_frame": [
                {"sequence": 1, "face_count": 2, "matched_face_count": 0},
                {"sequence": 2, "face_count": 1, "matched_face_count": 1},
            ],
            "worker_detect": {"p50_ms": 10, "p95_ms": 15},
            "client_capture_to_result": {"p50_ms": 20, "p95_ms": 25},
        },
    }
    second = {
        **first,
        "label": "coreml",
        "runtime": {"requested_execution_provider": "coreml"},
        "results": {
            **first["results"],
            "per_frame": [
                {"sequence": 1, "face_count": 2, "matched_face_count": 0},
                {"sequence": 2, "face_count": 2, "matched_face_count": 1},
            ],
        },
    }

    result = compare_reports(first, second)

    assert result["face_count_agreement_percent"] == 50
    assert result["matched_face_count_agreement_percent"] == 100


def test_compare_reports_rejects_different_inputs():
    left = {
        "workload": {"frame_sha256": ["a"]},
        "results": {"per_frame": [{"sequence": 1}]},
        "label": "left",
    }
    right = {
        "workload": {"frame_sha256": ["b"]},
        "results": {"per_frame": [{"sequence": 1}]},
        "label": "right",
    }

    try:
        compare_reports(left, right)
    except ValueError as exc:
        assert "different frames" in str(exc)
    else:
        raise AssertionError("different input reports should not compare")


def test_compare_reports_rejects_different_match_thresholds():
    base = {
        "workload": {"frame_sha256": ["same"]},
        "runtime": {
            "match_threshold": 0.65,
            "match_margin": 0.1,
            "stable_frame_count": 3,
            "stable_match_count": 2,
        },
        "results": {"per_frame": [{"sequence": 1}]},
        "label": "left",
    }
    changed = {
        **base,
        "label": "right",
        "runtime": {**base["runtime"], "match_threshold": 0.7},
    }

    try:
        compare_reports(base, changed)
    except ValueError as exc:
        assert "thresholds" in str(exc)
    else:
        raise AssertionError("different thresholds should not compare")
