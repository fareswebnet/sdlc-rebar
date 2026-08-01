---
name: sdlc-code-change-execution
description: Execute scoped code changes in a repository while preserving local patterns, tests, architecture boundaries, user changes, migration safety, and verification evidence. Use when implementing approved features, fixes, refactors, tests, migrations, or production remediations.
---

# SDLC Code Change Execution

## Purpose

Make disciplined changes that satisfy the spec and survive review.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Confirm the implementation plan or create one if missing.
2. Edit the smallest coherent set of files using existing patterns and helper APIs.
3. Add or update tests proportional to risk and blast radius.
4. Run targeted validation, then broader validation when shared behavior changed.
5. Summarize changed behavior, tests run, risks, and any unverified assumptions.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `code changes, tests, migrations, docs updates, validation notes`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not revert unrelated user changes or perform broad refactors outside the request.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
