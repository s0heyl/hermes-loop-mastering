#!/usr/bin/env python3
"""Score Hermes Loop Master artifacts in a project directory.

The harness validates the public artifact contract and, for Critical mode,
requires recorded behavioral evidence. It never executes commands copied from
artifacts; callers must run real verification separately.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from artifact_contract import (
    CONTRACT_VERSION,
    EVIDENCE_HEADER,
    MODE_REQUIREMENTS,
    REQUIRED_HANDOFF_SECTIONS,
    REQUIRED_LOOP_SECTIONS,
    REQUIRED_REVIEW_CHECKS,
)

SECRET_PATTERNS = [
    re.compile(r"\bgho_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(
        r"(?i)(api[_-]?key|secret|password|token)\s*=\s*['\"]?[^\s'\"]{12,}"
    ),
]

BEHAVIORAL_GATES = {
    "positive path": ("positive path",),
    "negative path": ("negative path",),
    "preservation path": ("preservation path",),
    "failure path": ("failure path",),
    "RED evidence": ("red evidence", " red ", "red→green", "red -> green"),
    "GREEN evidence": ("green evidence", " green ", "red→green", "red -> green"),
    "Independent Oracle": (
        "independent oracle",
        "oracle result",
        "oracle unavailable:",
    ),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def infer_mode(loop: str) -> str:
    match = re.search(
        r"## Classification\s+[`*]*\s*(tiny|standard|critical)\b",
        loop,
        re.I,
    )
    return match.group(1).lower() if match else "standard"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--mode", choices=sorted(MODE_REQUIREMENTS))
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail on any contract or behavioral issue, not only low score",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def evaluate(root: Path, requested_mode: str | None, strict: bool) -> dict:
    root = root.resolve()
    loop_dir = root / ".hermes-loop"
    if not loop_dir.exists():
        loop_dir = root

    loop = read(loop_dir / "LOOP.md")
    handoff = read(loop_dir / "HANDOFF.md")
    review = read(loop_dir / "REVIEW.md")
    features_path = loop_dir / "FEATURES.json"
    mode = requested_mode or infer_mode(loop)

    issues: list[str] = []
    score = 0
    max_score = 0

    max_score += len(REQUIRED_LOOP_SECTIONS)
    for section in REQUIRED_LOOP_SECTIONS:
        if section in loop:
            score += 1
        else:
            issues.append(f"LOOP.md missing section: {section}")

    max_score += 3
    if re.search(r"## Done When\s+(- \[[xX ]\] .+\n)+", loop):
        score += 1
    else:
        issues.append("LOOP.md Done When has no checkbox conditions")

    if EVIDENCE_HEADER in loop and re.search(
        r"\|\s*[^|]+\s*\|\s*`?[^|`]+`?\s*\|\s*(pass|ok|success|fail|blocked|skipped)",
        loop,
        re.I,
    ):
        score += 1
    else:
        issues.append("LOOP.md Evidence Log has no concrete command/check result")

    if "## Active Slice" in loop and re.search(r"## Active Slice\s+\S", loop):
        score += 1
    else:
        issues.append("LOOP.md Active Slice is empty")

    max_score += len(REQUIRED_HANDOFF_SECTIONS)
    for section in REQUIRED_HANDOFF_SECTIONS:
        if section in handoff:
            score += 1
        else:
            issues.append(f"HANDOFF.md missing section: {section}")

    max_score += len(REQUIRED_REVIEW_CHECKS) + 1
    review_lower = review.lower()
    for label in REQUIRED_REVIEW_CHECKS:
        if f"- [x] {label.lower()}" in review_lower:
            score += 1
        else:
            issues.append(f"REVIEW.md unchecked fake-done item: {label}")
    if "## Verdict" in review and re.search(
        r"## Verdict\s+(pass|needs-fix|blocked)", review, re.I
    ):
        score += 1
    else:
        issues.append("REVIEW.md missing verdict")

    if features_path.exists():
        max_score += 1
        try:
            data = json.loads(features_path.read_text(encoding="utf-8"))
            if isinstance(data, list) and all(
                "passes" in item for item in data if isinstance(item, dict)
            ):
                score += 1
            else:
                issues.append("FEATURES.json must be a list with passes fields")
        except Exception as exc:
            issues.append(f"FEATURES.json invalid JSON: {exc}")

    combined = "\n".join([loop, handoff, review]).lower()
    behavioral_passed = 0
    behavioral_required = 0
    if mode == "critical":
        behavioral_required = len(BEHAVIORAL_GATES)
        max_score += behavioral_required
        for label, needles in BEHAVIORAL_GATES.items():
            if any(needle.lower() in combined for needle in needles):
                score += 1
                behavioral_passed += 1
            else:
                issues.append(f"critical evidence missing: {label}")

    max_score += 1
    secret_hits: list[str] = []
    if loop_dir.exists():
        for path in loop_dir.rglob("*"):
            if not path.is_file() or path.stat().st_size > 1_000_000:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if any(pattern.search(text) for pattern in SECRET_PATTERNS):
                secret_hits.append(str(path.relative_to(loop_dir)))
    if secret_hits:
        issues.append("possible secrets found: " + ", ".join(secret_hits))
    else:
        score += 1

    ratio = score / max_score if max_score else 0.0
    passed = ratio >= 0.8 and not secret_hits
    if strict and issues:
        passed = False

    return {
        "contract_version": CONTRACT_VERSION,
        "root": str(root),
        "mode": mode,
        "strict": strict,
        "score": score,
        "max_score": max_score,
        "ratio": round(ratio, 6),
        "behavioral_gates_passed": behavioral_passed,
        "behavioral_gates_required": behavioral_required,
        "issues": issues,
        "secret_hits": secret_hits,
        "passed": passed,
    }


def main() -> int:
    args = parse_args()
    result = evaluate(Path(args.root), args.mode, args.strict)
    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            f"Score: {result['score']}/{result['max_score']} "
            f"({result['ratio']:.0%}) mode={result['mode']}"
        )
        if result["issues"]:
            print("Issues:")
            for issue in result["issues"]:
                print(f"- {issue}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
