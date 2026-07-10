---
contract_version: 1.0
---
# Loop State

## Goal
Reject forged webhook events without breaking valid signed delivery.

## Classification
critical

## Done When
- [x] Forged and replayed requests are rejected without side effects.
- [x] Valid and duplicate requests preserve the documented behavior.
- [x] Independent signature vectors agree with the implementation.

## Non-Goals
- Do not redesign the event store.

## Never Touch
- Credentials, production data, generated files, or dependency folders.

## Stop If
- Provider signature semantics cannot be verified from a public fixture.

## Plan
- [x] Reproduce the failure.
- [x] Add positive, negative, preservation, and failure tests.
- [x] Implement one narrow fix.
- [x] Run an Independent Oracle and broader regression suite.
- [x] Review and hand off.

## Active Slice
Verify signature parsing and replay boundaries against independent vectors.

## Evidence Log
| Time | Command / Check | Result | Notes |
|---|---|---|---|
| T0 | RED evidence: `python -m unittest tests.test_webhook_forgery` | fail | Negative path reproduced forged request acceptance. |
| T1 | GREEN evidence: `python -m unittest tests.test_webhook_forgery` | pass | Negative path and Failure path now reject without mutation. |
| T2 | Positive path and Preservation path: `python -m unittest tests.test_webhook_valid` | pass | Valid and duplicate deliveries retain contract. |
| T3 | Independent Oracle: provider public signature vectors | pass | Oracle result matches local verification. |
| T4 | `python -m unittest discover -s tests -v` | pass | Full related suite passes. |

## Decisions
| Decision | Reason | Date |
|---|---|---|
| Verify raw bytes | Provider signs raw request bodies | 2026-07-10 |
