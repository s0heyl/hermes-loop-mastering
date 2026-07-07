# Contributing

Thanks for helping improve Hermes Loop Mastering.

## Contribution rules

1. **Keep it public-safe.** Do not include private project names, customer data, credentials, internal paths, chat excerpts, or proprietary prompts.
2. **Make rules checkable.** Prefer concrete gates over generic advice. Example: "run `git diff --check`" is better than "be careful".
3. **Avoid agent-specific lock-in.** The skill is Hermes-native, but templates should remain readable by humans and other tools.
4. **No copied prompt packs.** Submit original wording or clearly licensed material with attribution.
5. **Add examples when adding behavior.** New rules should have a template change, fixture, or validator check when practical.

## Local validation

Run:

```bash
python3 scripts/validate_skill.py SKILL.md
python3 scripts/harness_check.py examples/good-loop
python3 scripts/harness_check.py examples/bad-loop || true
```

The good fixture should pass. The bad fixture should fail with useful messages.

## Suggested pull request format

```markdown
## Summary
- What changed?

## Why
- What failure mode does this reduce?

## Verification
- [ ] `python3 scripts/validate_skill.py SKILL.md`
- [ ] `python3 scripts/harness_check.py examples/good-loop`
- [ ] Bad fixture still fails for the expected reasons

## Public safety
- [ ] No private names, credentials, logs, or internal paths
- [ ] No copied proprietary prompt text
```
