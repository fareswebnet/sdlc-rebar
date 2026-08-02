---
name: releasepilot-pr-review
description: Review the ReleasePilot Signal Clustering PR against BDD traceability, TDD evidence, architecture boundaries, security review, UX states, feature flag rollout, rollback plan, and residual risk.
---

# ReleasePilot PR Review

## Purpose

Produce a merge recommendation grounded in evidence.

## Inputs

- diff
- BDD scenarios
- test output
- architecture notes
- security review
- feature flag definition
- PR body

## Output

Return:

- blocking findings
- non-blocking follow-ups
- required validation commands
- merge recommendation
- production gate status

## Guardrails

- Do not approve a PR that lacks tenant isolation evidence.
- Do not approve production rollout.
- Do not accept undocumented dependency or migration changes.
