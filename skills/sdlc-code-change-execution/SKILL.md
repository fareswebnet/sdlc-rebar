---
name: sdlc-code-change-execution
description: Execute scoped code changes in a repository while preserving local patterns, tests, architecture boundaries, user changes, migration safety, and verification evidence. Use when implementing approved features, fixes, refactors, tests, migrations, or production remediations.
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
