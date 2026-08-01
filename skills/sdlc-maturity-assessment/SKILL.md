---
name: sdlc-maturity-assessment
description: Assess SDLC maturity across product, UX, architecture, domain modeling, data, security, quality, delivery, reliability, observability, documentation, costs, and AI practices. Use when auditing an existing project, preparing an improvement roadmap, investor technical due diligence, or deciding which SDLC risks to address first.
---

# SDLC Maturity Assessment

## Purpose

Turn an uncertain project state into a prioritized improvement roadmap.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Inventory current artifacts, repo structure, tests, pipelines, security controls, and production signals.
2. Score each domain as Lean, Standard, Enterprise-ready, missing, or not applicable.
3. Separate critical risks from maturity nice-to-haves.
4. Produce a gap analysis with impact, effort, owner, and order of execution.
5. Connect every recommendation to evidence from the repo or named unknowns.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/governance/maturity-assessment.md, docs/governance/risk-register.md, docs/engineering/improvement-roadmap.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not assign maturity scores without evidence, explicit assumptions, or a clear not-observed note.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
