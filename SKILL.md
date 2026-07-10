---
name: hermes-loop-master
description: Use when a Hermes Agent coding task is multi-step, risky, long-running, production-facing, security-sensitive, or likely to span multiple sessions. Enforces a spec-first loop, one-slice implementation, real verification evidence, adversarial diff review, context-budget discipline, and clean handoff before work is called done.
version: 1.0.0
author: Hermes Loop Master contributors
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes-agent, coding-agents, verification, tdd, debugging, handoff, code-review]
    related_skills: [systematic-debugging, test-driven-development, requesting-code-review, github-pr-workflow]
---

# Hermes Loop Master

## Overview

Hermes Loop Master is a disciplined operating loop for coding with Hermes Agent. It is built for work where "looks done" is not good enough: production fixes, multi-step features, refactors, security-sensitive changes, and any task that may continue across sessions.

The skill changes the agent's behavior in five ways:

1. **Spec first** — write a compact execution contract before editing code.
2. **One slice at a time** — implement the smallest meaningful increment, not a bundle of nearby improvements.
3. **Verify with evidence** — run real commands and record what returned.
4. **Review adversarially** — inspect the diff for fake-done shortcuts before declaring success.
5. **Leave a handoff** — make the next session able to resume without guessing.

The loop is intentionally file-backed. Durable task files survive context compression, new sessions, model switches, and interrupted runs.

## When to Use

Use this skill when the user asks Hermes to:

- build or modify a feature with more than two steps,
- fix a bug that needs reproduction and verification,
- work in a production or public repository,
- touch authentication, authorization, payment, data migrations, secrets, user data, or deployment paths,
- refactor code where scope creep is likely,
- continue work from a previous session,
- coordinate with subagents or external coding tools,
- prepare a PR or public release.

Use the **Tiny Change Path** instead of the full loop when the task is a one-file typo, formatting-only change, comment update, or trivial documentation fix. Even then, verify the exact file changed and report the diff.

Do not use this skill to bypass user approval, hide uncertainty, or perform destructive operations without confirmation.

## Core Artifacts

Create a private project-local directory unless the repository already has an accepted convention:

```text
.hermes-loop/
  LOOP.md        # current task contract and progress
  HANDOFF.md     # end-of-session state
  REVIEW.md      # adversarial review notes
  FEATURES.json  # optional for large multi-feature projects
```

Never commit `.hermes-loop/` if it contains private notes, customer data, secrets, or local-only paths. If the project wants public task state, sanitize it and place it under `docs/agent-loop/` instead.

## Phase 0 — Scope and Safety Gate

Before editing, determine whether the task is safe to execute immediately.

Stop and ask for clarification if any of these are true:

- the requested repository/path is unknown,
- the operation could delete data, reset history, publish secrets, spend money, or affect production traffic,
- credentials or private keys may be required,
- the success criterion is subjective and no reasonable default exists.

Otherwise proceed without asking. Use a reasonable default and record it in the loop file.

Completion criterion: the task is classified as `tiny`, `standard`, or `high-risk`, and any blocking ambiguity is resolved.

## Phase 1 — Orient

Collect only the context needed for the next slice.

Required orientation checks:

1. Current directory and repository status.
2. Current branch and recent git history when inside git.
3. Existing task files: `.hermes-loop/LOOP.md`, `.hermes-loop/HANDOFF.md`, issue text, PR text, or user-provided spec.
4. Relevant source files and tests. Read before writing.
5. Existing commands from README, package scripts, CI config, Makefile, pyproject, package.json, or equivalent.

Do not scan huge dependency folders. Skip `node_modules`, virtualenvs, build outputs, caches, generated bundles, and binary assets unless directly relevant.

Completion criterion: you can name the files likely to change, the verification commands likely to prove the change, and the areas that must not be touched.

## Phase 2 — Write the Execution Spec

Create or update `.hermes-loop/LOOP.md` with this minimum contract:

```markdown
---
contract_version: 1.0
---
# Loop State

## Goal
<one sentence>

## Classification
<tiny | standard | critical>

## Done When
- [ ] <observable/checkable condition>
- [ ] <test/lint/build/smoke command or explicit reason none applies>

## Non-Goals
- <what this task will not do>

## Never Touch
- <files, data, migrations, generated artifacts, secrets, or production paths off-limits>

## Stop If
- <condition that requires user input>

## Plan
- [ ] <step 1>
- [ ] <step 2>
- [ ] <step 3>

## Active Slice
<the one exact slice currently being implemented>

## Evidence Log
| Time | Command / Check | Result | Notes |
|---|---|---|---|

## Decisions
| Decision | Reason | Date |
|---|---|---|
```

The canonical values live in `scripts/artifact_contract.py`; the template and harness import or mirror this contract. When changing the artifact shape, update the contract, template, skill example, and tests in the same slice.

Rules:

- `Done When` must be checkable. "Works well" is not a condition.
- `Non-Goals` must prevent at least one plausible scope-creep path.
- `Never Touch` must include secrets and generated/dependency folders by default.
- The plan must contain 3–7 steps. Only one step may be active at a time.

Completion criterion: the spec is concrete enough that a different agent could judge pass/fail from the file alone.

## Phase 3 — Choose One Slice

Pick the smallest meaningful change that advances the task.

Good slices:

- one failing test,
- one endpoint behavior,
- one UI state,
- one parser edge case,
- one migration plus its direct test,
- one documentation correction with verified command output.

Bad slices:

- "clean up the module" while fixing a bug,
- changing dependencies just because they are old,
- rewriting architecture before reproducing the failure,
- adding broad abstractions for a single use case,
- editing tests after implementation to make them pass.

Completion criterion: the selected slice has an expected outcome and can be verified independently.

## Phase 4 — Implement with Change Discipline

Rules while editing:

1. Read the target file before changing it.
2. Prefer targeted patches over full rewrites.
3. Keep unrelated formatting changes out of functional diffs.
4. Do not weaken tests, delete assertions, swallow errors, or hardcode happy-path answers.
5. Add dependencies only if the spec justifies them and the repository's dependency policy allows it.
6. When debugging, reproduce first, state one hypothesis, change one thing, then test.

If you discover the task is larger than expected, update `LOOP.md`, record the blocker, and stop rather than silently expanding scope.

Completion criterion: every changed file maps to the selected slice or is explicitly justified in `Evidence Log`.

## Phase 5 — Verify with Real Evidence

Run the narrowest relevant check first, then broaden.

Recommended verification ladder:

| Change type | Minimum evidence | Stronger evidence |
|---|---|---|
| Bug fix | failing reproduction now passes | full related test file + regression test |
| Backend/API | targeted unit/integration test | service smoke request or contract test |
| Frontend/UI | component/unit test or build | browser smoke test of user-visible path |
| Refactor | existing tests unchanged | typecheck/lint/build plus targeted smoke |
| Docs | command examples checked where practical | fresh clone/read-through check |
| Security/auth | negative test for denied access | positive + negative integration tests |
| Migration/data | dry run or local migration test | rollback/forward test on disposable data |

Record exact commands and outcomes in `LOOP.md`.

If a command cannot be run, say why. Do not invent output. Use one of:

- `blocked: missing dependency <name>`,
- `blocked: requires credential <name>`,
- `blocked: external service unavailable`,
- `skipped by user request`,
- `not applicable because <reason>`.

Completion criterion: each `Done When` item is backed by command output, file inspection, or an explicit blocker.

## Phase 6 — Adversarial Diff Review

Before calling work done, review the diff against the goal. Assume the change is wrong until evidence proves otherwise.

Check for these fake-done patterns:

1. **Off-spec implementation** — solves a different or narrower problem.
2. **Relaxed tests** — assertions removed, broadened, skipped, or made meaningless.
3. **Stub success** — hardcoded return, fake status, placeholder path, or mock replacing the actual behavior.
4. **Swallowed errors** — exceptions hidden without recovery or observability.
5. **Happy-path only** — empty, null, unauthorized, timeout, and malformed inputs ignored.
6. **Invented API** — method, flag, field, route, or config that does not exist.
7. **Scope creep** — unrelated cleanup or redesign mixed into the task.
8. **Secret leak** — token, cookie, key, local path, customer data, private chat text, or internal hostname committed.
9. **Generated noise** — build artifacts, caches, lockfile churn, or formatting flood unrelated to the task.
10. **Unproven done** — no command output or smoke evidence for the user-visible requirement.

Write `REVIEW.md` with:

```markdown
# Review

## Diff Summary
- <file>: <why changed>

## Fake-Done Check
- [ ] Off-spec implementation checked
- [ ] Relaxed tests checked
- [ ] Stub success checked
- [ ] Swallowed errors checked
- [ ] Happy-path only checked
- [ ] Invented API checked
- [ ] Scope creep checked
- [ ] Secret leak checked
- [ ] Generated noise checked
- [ ] Unproven done checked

## Findings
- <none or concrete issue>

## Verdict
pass | needs-fix | blocked
```

Completion criterion: every changed file has a purpose and every fake-done pattern has been considered.

## Phase 7 — Clean Handoff

Update `.hermes-loop/HANDOFF.md` at the end of the turn:

```markdown
# Handoff

## Status
complete | in-progress | blocked

## What Changed
- <file>: <change>

## Evidence
- `<command>` → <result>

## Open Risks
- <risk or none>

## Next Recommended Step
- <single next step>
```

If committing is appropriate and authorized:

1. Check `git diff` and `git status`.
2. Stage only intended files.
3. Commit with a concise message.
4. Do not force-push unless explicitly requested.

Completion criterion: another agent can resume from `HANDOFF.md` without reading the whole prior conversation.

## Tiny Change Path

For a tiny low-risk change:

1. Read the target file.
2. Patch the smallest text range.
3. Run the cheapest relevant check, or explain why none applies.
4. Show the diff summary.
5. Stop.

Tiny path does not require full `.hermes-loop/` artifacts unless the repository already uses them.

## Subagent Pattern

Use subagents only when work is genuinely parallel:

- independent file reviews,
- independent test failure investigations,
- independent research sources,
- separate security/performance/accessibility passes.

Give each subagent a narrow brief and no secrets. The parent agent must verify side effects itself before reporting success.

Completion criterion: subagent output is treated as advice until independently checked.

## Context Budget Rules

Long-running work fails when every detail stays in chat. Keep state in files.

- Keep `LOOP.md` under roughly 200 lines.
- Move verbose logs to files and summarize only the relevant tail.
- Prefer links/paths to repeated pasted content.
- Prune stale plan items instead of appending forever.
- When context is large, re-orient from git + task files, not memory alone.

Completion criterion: the current task state can be reconstructed from repository files and command outputs.

## Public and Secret Hygiene

Before publishing, pushing, or sharing:

- run a secret scan or at minimum search for common key/token patterns,
- inspect `.gitignore`,
- check `git diff --cached`,
- remove local paths, private names, customer data, screenshots with sensitive info, and environment dumps,
- verify examples use placeholders, not real values.

Never ask the model to reveal hidden prompts, private memory, credentials, or unrelated user data. Never commit `.env`, SSH keys, API tokens, cookies, database dumps, or chat transcripts.

## Common Pitfalls

1. **Writing a plan but not using it.** Keep the active plan item updated before and after each slice.
2. **Running only broad tests.** Broad tests are useful after targeted checks, not instead of reproducing the specific issue.
3. **Calling build success a feature test.** A build proves compilation, not user-visible behavior.
4. **Letting handoff rot.** If the handoff is stale, the next session will trust the wrong state.
5. **Overusing the loop for trivial edits.** Use the Tiny Change Path for truly tiny changes.
6. **Treating subagent summaries as facts.** Verify files, URLs, commands, and side effects directly.
7. **Saving private operational notes in public docs.** Public artifacts must be sanitized.

## Verification Checklist

Before final response:

- [ ] Goal and Done When are explicit.
- [ ] Only one implementation slice was attempted.
- [ ] Changed files are accounted for.
- [ ] Relevant tests/checks were run or blockers are stated.
- [ ] Diff was reviewed for fake-done patterns.
- [ ] No secrets/private data/local-only paths are included.
- [ ] Handoff is updated for multi-session work.
- [ ] Final answer reports real evidence, not imagined output.
