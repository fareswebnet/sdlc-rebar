---
name: sdlc-delivery-roadmap-backlog
description: Create delivery roadmaps, prioritized backlogs, vertical slices, ticket readiness checks, dependencies, release grouping, and outcome-based planning. Use after strategy, PRD, BDD, architecture, and design when turning decisions into executable work.
---

# SDLC Delivery Roadmap Backlog

## Purpose

Turn strategy and specs into small, valuable, buildable slices.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Connect each backlog item to outcome, requirement, behavior, design, architecture, and validation.
2. Slice vertically by user value and risk instead of technical layers.
3. Rank by impact, urgency, confidence, effort, dependencies, and cost of delay.
4. Define ticket readiness and split work that is too broad or ambiguous.
5. Maintain now/next/later roadmap with assumptions and decision checkpoints.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/delivery/roadmap.md, docs/delivery/backlog.md, docs/delivery/ticket-readiness.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not create tickets that are disconnected from product outcomes or validation.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
