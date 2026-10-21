#!/usr/bin/env python3
"""Compare two sanitized reports written by scripts/m1_benchmark.py."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_report(path: Path) -> dict:
    report = json.loads(path.read_text())
    if report.get("schema") != "m1-face-worker-benchmark/v1":
        raise ValueError(f"Unsupported benchmark report: {path}")
    return report


def compare_reports(left: dict, right: dict) -> dict:
    if left.get("workload") != right.get("workload"):
        raise ValueError("Reports use different frames, references, or stream settings")
    threshold_fields = (
        "match_threshold",
        "match_margin",
        "stable_frame_count",
        "stable_match_count",
    )
    if any(
        left["runtime"].get(field) != right["runtime"].get(field)
        for field in threshold_fields
    ):
        raise ValueError("Reports use different face-match thresholds or stability rules")
    left_frames = {
        row["sequence"]: row for row in left["results"].get("per_frame", [])
    }
    right_frames = {
        row["sequence"]: row for row in right["results"].get("per_frame", [])
    }
    common = sorted(left_frames.keys() & right_frames.keys())
    if not common:
        raise ValueError("Reports have no common processed frames")

    face_agreement = [
        left_frames[sequence]["face_count"] == right_frames[sequence]["face_count"]
        for sequence in common
    ]
    match_agreement = [
        left_frames[sequence]["matched_face_count"]
        == right_frames[sequence]["matched_face_count"]
        for sequence in common
    ]
    return {
        "same_workload": True,
        "runs": [left["label"], right["label"]],
        "providers": [
            left["runtime"].get("requested_execution_provider"),
            right["runtime"].get("requested_execution_provider"),
        ],
        "frames_common": len(common),
        "face_count_agreement_percent": round(
            100 * sum(face_agreement) / len(face_agreement), 2
        ),
        "matched_face_count_agreement_percent": round(
            100 * sum(match_agreement) / len(match_agreement), 2
        ),
        "timing_p50_p95_ms": {
            label: {
                "worker_detect": report["results"].get("worker_detect"),
                "client_capture_to_result": report["results"].get(
                    "client_capture_to_result"
                ),
            }
            for label, report in ((left["label"], left), (right["label"], right))
        },
        "throughput_frames_per_second": {
            left["label"]: left["results"].get("frames_per_second"),
            right["label"]: right["results"].get("frames_per_second"),
        },
        "model_initialization_ms": {
            left["label"]: left["runtime"].get("model_initialization_ms"),
            right["label"]: right["runtime"].get("model_initialization_ms"),
        },
        "service_startup_ms": {
            left["label"]: left["runtime"].get("service_startup_ms"),
            right["label"]: right["runtime"].get("service_startup_ms"),
        },
        "model_cache_warm_at_start": {
            left["label"]: left["runtime"].get("model_cache_warm_at_start"),
            right["label"]: right["runtime"].get("model_cache_warm_at_start"),
        },
        "missing_frames": {
            left["label"]: left["results"].get("frames_missing"),
            right["label"]: right["results"].get("frames_missing"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    args = parser.parse_args()
    left, right = load_report(args.first), load_report(args.second)
    print(json.dumps(compare_reports(left, right), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
