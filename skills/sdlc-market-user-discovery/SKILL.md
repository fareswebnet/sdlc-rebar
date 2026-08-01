---
name: sdlc-market-user-discovery
description: Plan and synthesize market research, user research, interviews, competitor review, segmentation, jobs-to-be-done, opportunity mapping, and evidence gathering for software products. Use before product strategy, PRD, MVP scope, or when a team is building from weak assumptions.
---

# SDLC Market User Discovery

## Purpose

Replace internal guesses with evidence and well-labeled uncertainty.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Define segments, personas, jobs, and research questions.
2. Collect market, competitor, user, support, analytics, and sales signals where available.
3. Separate observed facts from interpretations and hypotheses.
4. Identify opportunities, objections, switching costs, and non-consumption.
5. Summarize what should change in product scope, messaging, or roadmap.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/product/discovery.md, docs/product/research-plan.md, docs/product/opportunity-map.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not treat unvalidated assumptions as customer evidence.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
