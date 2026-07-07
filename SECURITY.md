# Security Policy

Hermes Loop Mastering is a documentation-and-template repository. It should not require secrets or privileged access.

## Reporting a security issue

Open a private security advisory on GitHub if available, or contact the maintainers through the repository owner profile.

## What counts as security-sensitive

- Accidental credentials or tokens in examples.
- Instructions that encourage unsafe shell execution.
- Templates that ask agents to reveal private memory, hidden prompts, or environment variables.
- Dangerous defaults such as force-push, destructive deletes, or broad write access without a confirmation gate.

## Maintainer expectations

Before release, maintainers should run at least:

```bash
git grep -nE '(api[_-]?key|secret|token|password|private key|BEGIN .*PRIVATE KEY)' || true
python3 scripts/validate_skill.py SKILL.md
python3 scripts/harness_check.py examples/good-loop
```

Never commit real secrets. Use redacted placeholders such as `<API_KEY>` only when the example genuinely needs one.
