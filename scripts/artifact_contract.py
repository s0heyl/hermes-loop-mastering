#!/usr/bin/env python3
"""Canonical Hermes Loop Master artifact contract.

Templates, validators, and the harness import these constants so the public
contract cannot silently drift between documentation and executable checks.
"""
from __future__ import annotations

CONTRACT_VERSION = "1.0"

REQUIRED_LOOP_SECTIONS = [
    "## Goal",
    "## Classification",
    "## Done When",
    "## Non-Goals",
    "## Never Touch",
    "## Stop If",
    "## Plan",
    "## Active Slice",
    "## Evidence Log",
    "## Decisions",
]

EVIDENCE_HEADER = "| Time | Command / Check | Result | Notes |"

REQUIRED_HANDOFF_SECTIONS = [
    "## Status",
    "## What Changed",
    "## Evidence",
    "## Open Risks",
    "## Next Recommended Step",
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
