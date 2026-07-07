#!/usr/bin/env python3
"""Score Hermes Loop Mastering artifacts in a project directory.

This is intentionally lightweight: it checks for durable loop files and
verification evidence. It does not claim to prove code correctness.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_LOOP_SECTIONS = [
    "## Goal",
    "## Done When",
    "## Non-Goals",
    "## Never Touch",
    "## Stop If",
    "## Plan",
    "## Evidence Log",
]

REQUIRED_REVIEW_CHECKS = [
    "Off-spec implementation checked",
    "Relaxed tests checked",
    "Stub success checked",
    "Swallowed errors checked",
    "Happy-path only checked",
    "Invented API checked",
    "Scope creep checked",
    "Secret leak checked",
    "Generated noise checked",
    "Unproven done checked",
]

SECRET_PATTERNS = [
    re.compile(r"gho_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*=\s*['\"]?[^\s'\"]{12,}"),
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def checked(text: str, label: str) -> bool:
    return f"- [x] {label}" in text.lower() or f"- [X] {label}" in text


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    loop_dir = root / ".hermes-loop"
    if not loop_dir.exists():
        # examples may store files at root for readability
        loop_dir = root

    issues: list[str] = []
    score = 0
    max_score = 0

    loop = read(loop_dir / "LOOP.md")
    handoff = read(loop_dir / "HANDOFF.md")
    review = read(loop_dir / "REVIEW.md")
    features_path = loop_dir / "FEATURES.json"

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

    if "| Time | Command / Check | Result | Notes |" in loop and re.search(r"\|\s*[^|]+\s*\|\s*`?[^|`]+`?\s*\|\s*(pass|ok|success|fail|blocked|skipped)", loop, re.I):
        score += 1
    else:
        issues.append("LOOP.md Evidence Log has no concrete command/check result")

    if "## Active Slice" in loop and re.search(r"## Active Slice\s+\S", loop):
        score += 1
    else:
        issues.append("LOOP.md Active Slice is empty")

    max_score += 5
    for section in ["## Status", "## What Changed", "## Evidence", "## Open Risks", "## Next Recommended Step"]:
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
    if "## Verdict" in review and re.search(r"## Verdict\s+(pass|needs-fix|blocked)", review, re.I):
        score += 1
    else:
        issues.append("REVIEW.md missing verdict")

    if features_path.exists():
        max_score += 1
        try:
            data = json.loads(features_path.read_text(encoding="utf-8"))
            if isinstance(data, list) and all("passes" in item for item in data if isinstance(item, dict)):
                score += 1
            else:
                issues.append("FEATURES.json must be a list with passes fields")
        except Exception as exc:
            issues.append(f"FEATURES.json invalid JSON: {exc}")

    # Secret scan text files in the loop directory.
    max_score += 1
    secret_hits = []
    for path in loop_dir.rglob("*"):
        if not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                secret_hits.append(str(path.relative_to(loop_dir)))
    if secret_hits:
        issues.append("possible secrets found: " + ", ".join(secret_hits))
    else:
        score += 1

    ratio = score / max_score if max_score else 0
    print(f"Score: {score}/{max_score} ({ratio:.0%})")
    if issues:
        print("Issues:")
        for issue in issues:
            print(f"- {issue}")

    if ratio < 0.8 or any("possible secrets" in item for item in issues):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
