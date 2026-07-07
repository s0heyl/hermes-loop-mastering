# Loop State

## Goal
Add input trimming to a greeting helper without changing public output format.

## Classification
standard

## Done When
- [x] Empty or whitespace-only names return `Hello, stranger!`
- [x] Non-empty names are trimmed before greeting
- [x] Targeted test command passes

## Non-Goals
- Do not redesign the greeting module.
- Do not add external dependencies.

## Never Touch
- `.env`, secrets, private keys, credentials
- dependency folders such as `node_modules/`, `.venv/`, `venv/`
- generated outputs such as `dist/`, `build/`, coverage folders, caches

## Stop If
- Existing tests fail outside the greeting helper behavior.

## Plan
- [x] Orient: read greeting helper and existing tests
- [x] Add regression tests for whitespace input
- [x] Implement one smallest meaningful slice
- [x] Run targeted verification
- [x] Review diff adversarially
- [x] Update handoff

## Active Slice
Trim greeting helper input and preserve fallback behavior for blank names.

## Evidence Log
| Time | Command / Check | Result | Notes |
|---|---|---|---|
| 2026-01-01T00:00:00Z | `python3 -m pytest tests/test_greeting.py -q` | pass | 3 passed |
| 2026-01-01T00:00:05Z | `git diff --check` | ok | no whitespace errors |

## Decisions
| Decision | Reason | Date |
|---|---|---|
| Keep implementation dependency-free | Existing helper is pure Python | 2026-01-01 |
