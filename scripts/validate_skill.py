#!/usr/bin/env python3
"""Validate a Hermes/Agent Skills SKILL.md file."""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    sys.exit(2)

REQUIRED_HEADINGS = [
    "# Hermes Loop Mastering",
    "## Overview",
    "## When to Use",
    "## Verification Checklist",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "SKILL.md")
    if not path.exists():
        fail(f"not found: {path}")

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("frontmatter must start at byte 0 with ---")

    match = re.search(r"\n---\s*\n", text[4:])
    if not match:
        fail("frontmatter closing --- not found")

    # match indexes are relative to text[4:]
    close_start = match.start() + 4
    frontmatter = text[4:close_start]
    body = text[match.end() + 4 :]

    try:
        meta = yaml.safe_load(frontmatter)
    except Exception as exc:
        fail(f"frontmatter YAML parse error: {exc}")

    if not isinstance(meta, dict):
        fail("frontmatter must parse to a mapping")

    for key in ["name", "description", "version", "author", "license"]:
        if not meta.get(key):
            fail(f"missing frontmatter key: {key}")

    name = str(meta["name"])
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
        fail("name must be lowercase kebab-case and <=64 characters")

    description = str(meta["description"])
    if len(description) > 1024:
        fail("description exceeds 1024 characters")
    if not description.startswith("Use when "):
        fail("description should start with 'Use when '")

    if not body.strip():
        fail("body is empty")
    if len(text) > 100_000:
        fail("SKILL.md exceeds 100,000 characters")

    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            fail(f"missing required heading: {heading}")

    forbidden = [
        "api_key=",
        "BEGIN PRIVATE KEY",
        "gho_",
        "sk-",
        "/home/node/.openclaw",
        "/root/.hermes/cache",
    ]
    lowered = text.lower()
    for needle in forbidden:
        if needle.lower() in lowered:
            fail(f"forbidden/private pattern found: {needle}")

    print(f"OK: {path} is a valid Hermes skill ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
