---
name: sdlc-implementation-planning
description: Plan implementation for scoped code changes by identifying affected files, architecture boundaries, data migrations, tests, risks, rollback, validation commands, and sequencing. Use before modifying a repository for features, fixes, refactors, migrations, or production changes.
---

# SDLC Implementation Planning

## Purpose

Make code work predictable before editing files.

## Workflow

1. Read relevant specs, code, tests, architecture notes, and local conventions.
2. Map impacted modules, contracts, data, permissions, and user-visible behavior.
3. Choose the smallest implementation sequence that preserves working states.
4. Define tests, manual checks, migration safety, and rollback path.
5. Call out assumptions and blockers before execution.

## Outputs

- Primary artifacts: `docs/engineering/implementation-plan.md, docs/quality/validation-plan.md`.

## Guardrails

- Do not implement from memory when the repo can provide the answer.
