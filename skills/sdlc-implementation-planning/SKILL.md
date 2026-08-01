---
name: sdlc-implementation-planning
description: Plan implementation for scoped code changes by identifying affected files, architecture boundaries, data migrations, tests, risks, rollback, validation commands, and sequencing. Use before modifying a repository for features, fixes, refactors, migrations, or production changes.
---

# SDLC Implementation Planning

## Purpose

Make code work predictable before editing files.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Read relevant specs, code, tests, architecture notes, and local conventions.
2. Map impacted modules, contracts, data, permissions, and user-visible behavior.
3. Choose the smallest implementation sequence that preserves working states.
4. Define tests, manual checks, migration safety, and rollback path.
5. Call out assumptions and blockers before execution.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/engineering/implementation-plan.md, docs/quality/validation-plan.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not implement from memory when the repo can provide the answer.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
