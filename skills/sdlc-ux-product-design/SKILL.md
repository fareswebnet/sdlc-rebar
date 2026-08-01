---
name: sdlc-ux-product-design
description: Design UX journeys, information architecture, user flows, states, edge cases, onboarding, permissions, error handling, empty states, and accessibility-aware product interactions. Use before UI implementation, design review, PRD finalization, or when a workflow feels confusing or incomplete.
---

# SDLC UX Product Design

## Purpose

Make workflows usable before they become tickets and screens.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Map actors, goals, scenarios, journey phases, actions, questions, and friction.
2. Design primary, alternate, empty, loading, error, permission, success, conflict, and degraded states.
3. Check information architecture, navigation, hierarchy, forms, filters, and search.
4. Tie UX decisions to BDD behavior and product metrics.
5. Flag research, accessibility, and support risks before implementation.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/ux/journeys.md, docs/ux/flows.md, docs/ux/state-matrix.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not approve a flow that lacks error, empty, loading, permission, and success states.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
