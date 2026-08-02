---
name: releasepilot-tdd
description: Write failing tests for the accepted ReleasePilot Signal Clustering BDD scenarios before production code changes, then record red-test evidence and the expected implementation boundary.
---

# ReleasePilot TDD

## Purpose

Force behavior-first development.

## Workflow

1. Read the accepted BDD scenarios.
2. Write domain tests first.
3. Write UI state tests for review workflow states.
4. Run tests and confirm they fail for the expected missing behavior.
5. Record failing commands and assertion intent.
6. Hand off to implementation only after the red gate is documented.

## Outputs

- `tests/domain/signal-clustering.test.ts`
- `tests/components/signal-cluster-review.test.tsx`
- `docs/quality/acceptance-tests.md`

## Guardrails

- Do not edit implementation files.
- Do not weaken BDD scenarios to make tests easier.
- Do not skip tenant isolation tests.
