#!/usr/bin/env python3
"""Compare two Hermes Loop Master benchmark snapshots.

Snapshots contain observed metrics only; this script never invents or executes
benchmark results. Exit 1 means a correctness regression, exit 2 invalid input.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_KEYS = {
    "name",
    "hidden_passed",
    "hidden_total",
    "visible_passed",
    "visible_total",
    "elapsed_seconds",
    "tool_calls",
}


def load_snapshot(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"snapshot must be an object: {path}")
    missing = sorted(REQUIRED_KEYS - data.keys())
    if missing:
        raise ValueError(f"missing required keys in {path}: {', '.join(missing)}")
    for prefix in ("hidden", "visible"):
        passed = data[f"{prefix}_passed"]
        total = data[f"{prefix}_total"]
        if not isinstance(passed, int) or not isinstance(total, int):
            raise ValueError(f"{prefix} counts must be integers in {path}")
        if total <= 0 or passed < 0 or passed > total:
            raise ValueError(f"invalid {prefix} counts in {path}")
    if data["elapsed_seconds"] <= 0 or data["tool_calls"] < 0:
        raise ValueError(f"invalid efficiency metrics in {path}")
    return data


def percent_delta(before: float, after: float) -> float:
    return round((after / before - 1.0) * 100.0, 3) if before else 0.0


def compare(baseline: dict, candidate: dict) -> dict:
    base_hidden = baseline["hidden_passed"] / baseline["hidden_total"]
    cand_hidden = candidate["hidden_passed"] / candidate["hidden_total"]
    base_visible = baseline["visible_passed"] / baseline["visible_total"]
    cand_visible = candidate["visible_passed"] / candidate["visible_total"]
    quality_gate = cand_hidden >= base_hidden and cand_visible >= base_visible
    return {
        "baseline": baseline["name"],
        "candidate": candidate["name"],
        "baseline_hidden_accuracy": round(base_hidden, 6),
        "candidate_hidden_accuracy": round(cand_hidden, 6),
        "hidden_accuracy_delta_points": round((cand_hidden - base_hidden) * 100, 3),
        "baseline_visible_accuracy": round(base_visible, 6),
        "candidate_visible_accuracy": round(cand_visible, 6),
        "visible_accuracy_delta_points": round((cand_visible - base_visible) * 100, 3),
        "elapsed_delta_percent": percent_delta(
            float(baseline["elapsed_seconds"]), float(candidate["elapsed_seconds"])
        ),
        "tool_call_delta_percent": percent_delta(
            float(baseline["tool_calls"]), float(candidate["tool_calls"])
        ),
        "quality_gate_passed": quality_gate,
    }


def markdown(result: dict) -> str:
    status = "PASS" if result["quality_gate_passed"] else "FAIL"
    return "\n".join(
        [
            f"# Benchmark comparison: {result['baseline']} → {result['candidate']}",
            "",
            "| Metric | Delta |",
            "|---|---:|",
            f"| Hidden accuracy | {result['hidden_accuracy_delta_points']:+.3f} points |",
            f"| Visible accuracy | {result['visible_accuracy_delta_points']:+.3f} points |",
            f"| Elapsed time | {result['elapsed_delta_percent']:+.3f}% |",
            f"| Tool calls | {result['tool_call_delta_percent']:+.3f}% |",
            "",
            f"Quality gate: **{status}**",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        result = compare(load_snapshot(args.baseline), load_snapshot(args.candidate))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True) if args.as_json else markdown(result))
    return 0 if result["quality_gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
