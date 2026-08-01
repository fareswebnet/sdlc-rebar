---
name: sdlc-domain-modeling
description: Discover and model the business domain using DDD vocabulary, ubiquitous language, entities, value objects, aggregates, invariants, state transitions, policies, and domain services. Use before architecture, database design, BDD, API contracts, or implementation in domains with meaningful business rules.
---

# SDLC Domain Modeling

## Purpose

Make the business model explicit before the software model hardens.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Extract domain terms, actors, actions, lifecycle states, and policies.
2. Identify entities, value objects, aggregates, commands, events, and invariants.
3. Separate domain rules from UI, persistence, integration, and reporting concerns.
4. Find ambiguous terms and align them with a ubiquitous language.
5. Feed bounded contexts, BDD scenarios, database design, and API contracts.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/architecture/domain-model.md, docs/architecture/ubiquitous-language.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not design tables, APIs, or services before the core domain terms and invariants are clear.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
