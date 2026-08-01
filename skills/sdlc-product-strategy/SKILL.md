---
name: sdlc-product-strategy
description: Define product strategy, target outcomes, MVP scope, appetite, positioning, roadmap horizons, success metrics, and strategic trade-offs for software projects. Use after initial discovery and before PRD, architecture, backlog slicing, or investor/product planning.
---

# SDLC Product Strategy

## Purpose

Choose what is worth building and what should be deliberately excluded.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Translate discovery into strategic outcomes and target users.
2. Set appetite, constraints, non-goals, and success metrics.
3. Compare MVP, wedge, platform, and enterprise-ready paths.
4. Identify strategic risks and decision points.
5. Produce a roadmap that explains why each item matters.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/product/strategy.md, docs/product/mvp-scope.md, docs/delivery/roadmap.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not add scope without naming the outcome it supports and the trade-off it creates.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
