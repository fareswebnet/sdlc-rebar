---
name: sdlc-documentation-knowledge
description: Create and maintain repo-first documentation architecture, onboarding guides, API docs, ADRs, runbooks, user docs, knowledge base updates, and stale-doc checks. Use when documenting a project, onboarding developers, preparing support, exposing APIs, or making SDLC artifacts living and versioned.
---

# SDLC Documentation Knowledge

## Purpose

Keep knowledge close to the work and useful under pressure.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Define documentation audiences: developers, product, operators, support, users, auditors, and investors.
2. Keep docs short, linked, versioned, and tied to code/specs/decisions.
3. Create onboarding, API, architecture, runbook, release, and user documentation as needed.
4. Detect stale docs by comparing claims to repo, tests, configs, and production behavior.
5. Prefer repo-first documentation for engineering truth.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/README.md, docs/engineering/developer-onboarding.md, docs/operations/runbooks/, docs/architecture/adr/`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not create documents without owner, audience, update trigger, and link to the relevant artifact or code.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
