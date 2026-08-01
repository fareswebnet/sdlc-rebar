---
name: sdlc-architecture-rfc
description: Create architecture RFCs, C4-style diagrams, ADR candidates, viewpoints, constraints, risks, trade-off tables, and architecture review packets. Use when choosing or changing architecture style, platform boundaries, module structure, integrations, data ownership, or production-critical technical decisions.
---

# SDLC Architecture RFC

## Purpose

Make significant architecture choices explicit, reviewable, and traceable.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Identify stakeholders, concerns, quality attributes, constraints, and context.
2. Describe current state and proposed architecture at the right abstraction level.
3. Compare alternatives, consequences, reversibility, and migration path.
4. Use C4-style context/container/component views when diagrams help communication.
5. Promote accepted decisions into ADRs and implementation constraints.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/architecture/rfc/, docs/architecture/adr/, docs/architecture/c4/`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not present architecture as a preference; document the forces, trade-offs, and consequences.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
