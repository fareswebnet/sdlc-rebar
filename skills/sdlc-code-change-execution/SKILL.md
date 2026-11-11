---
name: sdlc-code-change-execution
description: Implement scoped code changes preserving local patterns, tests, boundaries, and user changes, with verification evidence. Use for approved features, fixes, refactors, or migrations.
---

# SDLC Code Change Execution

## Purpose

Make disciplined changes that satisfy the spec and survive review.

## Workflow

1. Confirm the implementation plan or create one if missing.
2. Edit the smallest coherent set of files using existing patterns and helper APIs.
3. Add or update tests proportional to risk and blast radius.
4. Run targeted validation, then broader validation when shared behavior changed.
5. Summarize changed behavior, tests run, risks, and any unverified assumptions.

## Outputs

- Primary artifacts: `code changes, tests, migrations, docs updates, validation notes`.

## Guardrails

- Do not revert unrelated user changes or perform broad refactors outside the request.
