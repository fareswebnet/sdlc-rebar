---
name: sdlc-product-analytics-experimentation
description: Design product analytics, tracking plans, event taxonomy, funnels, activation, retention, cohorts, experiments, feature flags, metric governance, data quality checks, dashboards, and business intelligence readiness. Use when defining product success, analytics instrumentation, experiments, or investor/product metrics.
---

# SDLC Product Analytics Experimentation

## Purpose

Measure whether the product creates value, not only whether the system works.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Define north-star, activation, retention, conversion, usage, satisfaction, and business metrics.
2. Create event taxonomy with source, owner, properties, privacy classification, and expected dashboards.
3. Design experiments with hypothesis, audience, success metric, guardrails, and bias risks.
4. Check data quality: completeness, duplicates, freshness, identity stitching, and metric definitions.
5. Connect product analytics to roadmap and support feedback.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/product/metrics.md, docs/analytics/tracking-plan.md, docs/analytics/experiments.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not accept an important metric without a definition, owner, source of truth, and known limitations.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
