---
name: sdlc-quality-test-strategy
description: Define quality strategy, acceptance tests, unit tests, integration tests, contract tests, e2e tests, regression risk, exploratory testing, non-functional testing, and quality gates. Use when planning validation for a feature, release, refactor, incident fix, architecture change, or BDD specification.
---

# SDLC Quality Test Strategy

## Purpose

Test what matters by risk, behavior, and quality attributes rather than coverage theater.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Map requirements, BDD scenarios, architecture boundaries, and risk areas.
2. Choose the right test level for each behavior: unit, integration, contract, e2e, exploratory, or manual.
3. Define non-functional checks for security, performance, accessibility, reliability, and compatibility where relevant.
4. Prioritize regression coverage around critical user and business workflows.
5. Set a quality gate for merge and release.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/quality/test-strategy.md, docs/quality/acceptance-tests.md, docs/quality/regression-risk.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not equate high coverage percentage with sufficient product quality.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
