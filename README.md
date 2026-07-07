# Hermes Loop Mastering

**A public, Hermes-native skill for reliable long-running coding work.**

Hermes Loop Mastering turns vague coding requests into a disciplined loop:

1. define the contract,
2. make one small change,
3. verify with real commands,
4. review the diff adversarially,
5. leave a clean handoff for the next session.

It is designed for Hermes Agent users, but the workflow is plain Markdown and shell-friendly enough for other coding agents and human teams.

> Status: initial public release. Contributions welcome.

## Why this exists

Coding agents are good at producing code. They are less reliable at knowing when the work is truly done. Common failure modes:

- solving a nearby problem instead of the requested one,
- making several unrelated changes in one pass,
- weakening tests to get green output,
- declaring success after a build starts but before the feature works,
- losing context across sessions,
- leaking secrets or internal notes into commits.

Hermes Loop Mastering gives the agent a small operating system for coding tasks: durable task files, strict verification gates, and explicit stop rules.

## What is inside

```text
.
├── SKILL.md                         # The Hermes skill
├── templates/
│   ├── LOOP.md                      # Task loop state file
│   ├── FEATURES.json                # Optional feature ledger for long projects
│   ├── HANDOFF.md                   # End-of-session handoff template
│   └── REVIEW.md                    # Adversarial diff review checklist
├── scripts/
│   ├── validate_skill.py            # Validates SKILL.md metadata and structure
│   └── harness_check.py             # Scores loop artifacts in a project
├── examples/
│   ├── good-loop/                   # Example project state that should pass
│   └── bad-loop/                    # Example project state that should fail
├── CONTRIBUTING.md
├── SECURITY.md
└── LICENSE
```

## Install for Hermes

Clone or download this repository, then copy it into your Hermes skills folder:

```bash
mkdir -p ~/.hermes/skills/software-development
cp -R hermes-loop-mastering ~/.hermes/skills/software-development/hermes-loop-mastering
```

Start a fresh Hermes session so skills are reloaded, then ask for it explicitly when needed:

```text
Use the hermes-loop-mastering skill to implement this feature safely...
```

If you maintain a shared skill registry, you can also import the folder as an Agent Skills compatible `SKILL.md` package.

## Quick start in a repo

From your project root:

```bash
mkdir -p .hermes-loop
cp /path/to/hermes-loop-mastering/templates/LOOP.md .hermes-loop/LOOP.md
cp /path/to/hermes-loop-mastering/templates/HANDOFF.md .hermes-loop/HANDOFF.md
```

Then ask Hermes:

```text
Use Hermes Loop Mastering. Read .hermes-loop/LOOP.md, fill the goal and Done When section, implement exactly one next step, run real verification, update HANDOFF.md, and stop.
```

For larger projects, add `FEATURES.json` and let each session complete one entry at a time.

## The loop contract

Every coding pass follows this contract:

| Phase | Required evidence |
|---|---|
| Orient | Current branch, dirty state, task file, relevant files read |
| Specify | Goal, Done When, Never Touch, Stop If |
| Plan | 3–7 concrete steps with exactly one `in_progress` item |
| Act | Smallest implementation slice; no unrelated cleanup |
| Verify | Real command output: tests, lint/typecheck/build, smoke check as applicable |
| Review | Diff checked against fake-done patterns and secret leakage |
| Handoff | Changed files, commands run, open risks, next recommended step |

## Included checks

Validate the skill file:

```bash
python3 scripts/validate_skill.py SKILL.md
```

Score a project's loop artifacts:

```bash
python3 scripts/harness_check.py examples/good-loop
python3 scripts/harness_check.py examples/bad-loop
```

Expected behavior:

- `good-loop` passes with a high score.
- `bad-loop` fails and lists missing verification/handoff fields.

## What this skill does not do

- It does not grant extra permissions.
- It does not install MCP servers.
- It does not require any external API keys.
- It does not claim that prompts alone guarantee correctness.
- It does not replace real tests, CI, code review, or human product judgment.

## Recommended use cases

- production bug fixes,
- multi-step features,
- refactors with risk of scope creep,
- agent handoffs across sessions,
- security-sensitive changes,
- public/open-source contributions where reviewability matters.

For one-line edits, use judgment: the full loop may be heavier than necessary. The skill includes a lightweight path for tiny changes.

## Public safety principles

This repository is intentionally generic:

- no private project names,
- no customer data,
- no credentials,
- no environment-specific paths,
- no private operational notes,
- no copied private prompts.

Please keep contributions public-safe.

## Roadmap

- More language-specific verification recipes.
- Optional GitHub Actions workflow once maintainers have appropriate token scopes.
- More example fixtures.
- A small installer that copies templates without overwriting existing files.
- Benchmarks on real open-source tasks.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
