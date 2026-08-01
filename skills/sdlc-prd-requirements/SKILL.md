---
name: sdlc-prd-requirements
description: Create and refine PRDs, requirements, user stories, acceptance criteria, assumptions, open questions, constraints, and out-of-scope decisions for software products. Use when turning strategy or discovery into precise, testable, non-ambiguous requirements before BDD, architecture, design, tickets, or implementation.
---

# SDLC PRD Requirements

## Purpose

Create requirements that are specific enough to build and test, without over-specifying implementation.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Capture goal, background, users, scope, non-goals, and constraints.
2. Write requirements as observable behavior or measurable quality expectations.
3. Tag every assumption, open question, dependency, and decision owner.
4. Connect requirements to BDD examples and product metrics.
5. Revise requirements when design, architecture, or implementation exposes ambiguity.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/product/prd.md, docs/product/open-questions.md, docs/product/requirements-traceability.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not accept vague verbs like improve, optimize, support, or handle unless the observable behavior is defined.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
