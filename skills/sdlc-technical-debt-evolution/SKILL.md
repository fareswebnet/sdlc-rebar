---
name: sdlc-technical-debt-evolution
description: Inventory technical debt, codebase health, refactoring plans, architecture evolution, legacy modernization, documentation freshness, maintainability risks, and migration strategies. Use when a codebase is slowing down, architecture boundaries are eroding, tests are weak, or a modernization path is needed.
---

# SDLC Technical Debt Evolution

## Purpose

Manage debt as a portfolio of risks, not a vague cleanup wish list.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Classify debt across code, tests, architecture, data, infra, security, UX, docs, and operations.
2. Estimate impact, cost of inaction, correction effort, risk, owner, and time horizon.
3. Design incremental refactors with tests, compatibility, rollback, and migration safety.
4. Record architecture evolution decisions and sunset plans.
5. Tie debt reduction to delivery speed, reliability, security, or product outcomes.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/engineering/tech-debt.md, docs/engineering/refactoring-plan.md, docs/architecture/adr/`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not schedule refactoring without a measurable risk reduction or delivery benefit.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
