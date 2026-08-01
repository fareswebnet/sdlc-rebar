---
name: sdlc-application-architecture
description: Design application architecture including modular monoliths, layered architecture, hexagonal ports/adapters, clean architecture, services, background jobs, CQRS, event-driven flows, dependency rules, and module boundaries. Use after domain/context modeling and before implementation or large refactors.
---

# SDLC Application Architecture

## Purpose

Choose a structure the team can build, test, and evolve.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Start from bounded contexts, domain rules, runtime constraints, and team ownership.
2. Choose the simplest architecture style that satisfies quality attributes and change pressure.
3. Define modules, layers, dependency direction, adapters, services, jobs, and integration points.
4. Document transaction boundaries, failure handling, and deployment implications.
5. Create ADRs for choices that constrain future code.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/architecture/application-architecture.md, docs/architecture/module-boundaries.md, docs/architecture/adr/`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Default to modular monolith plus clear boundaries unless scale, teams, regulation, or runtime constraints justify more distributed complexity.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
