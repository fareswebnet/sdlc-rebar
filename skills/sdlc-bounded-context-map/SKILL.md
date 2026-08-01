---
name: sdlc-bounded-context-map
description: Create DDD bounded context maps, ownership boundaries, upstream/downstream relationships, shared kernels, anti-corruption layers, context interfaces, and team/data ownership. Use when a product has multiple domains, modules, teams, services, tenants, or integration boundaries.
---

# SDLC Bounded Context Map

## Purpose

Prevent one vague model from spreading across unrelated parts of the system.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Group domain language and behavior into coherent contexts.
2. Define each context's owner, purpose, data ownership, and public contracts.
3. Map upstream/downstream dependencies and translation needs.
4. Choose integration patterns such as direct call, event, ACL, shared kernel, or published language.
5. Record boundary decisions as ADRs when they affect architecture or teams.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/architecture/context-map.md, docs/architecture/bounded-contexts.md, docs/architecture/adr/`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not split by technical layer when the real boundary is business capability or data ownership.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
