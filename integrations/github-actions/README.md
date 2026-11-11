# GitHub Actions Integration

Use GitHub Actions for deterministic gates around autonomous or semi-autonomous coding.

## Recommended Gates

- lint and formatting
- unit tests
- integration or contract tests
- BDD acceptance checks when available
- type checks
- dependency and license review
- secret scanning
- security scan
- build artifact verification
- preview deployment
- release readiness checklist

## PR Template Hooks

Require each autonomous PR to include:

- product or issue link
- BDD examples or acceptance criteria
- architecture and data impact
- tests run
- screenshots or preview link for UI changes
- migration and rollback notes
- security and privacy impact
- residual risk

## Agent Runs In CI

Use narrow scripted agent runs for summaries and review support:

```bash
codex exec --sandbox workspace-write \
  "Use sdlc-code-review to review this PR diff. Return blocking findings first, then missing tests, then residual risk."
```

Keep CI agent runs non-destructive. They can comment, summarize, or open follow-up issues, but should not deploy to production without a separate human-approved workflow.

## Branch Protection

Require:

- at least one human approval for production-impacting changes
- passing CI checks
- no unresolved security blocker
- migration approval when database changes exist
- release-manager sign-off for deployment branches
