---
name: sdlc-bdd-specifications
description: Run behavior discovery, example mapping, acceptance criteria, Gherkin Given/When/Then scenarios, and living documentation for product behavior. Use when requirements need clarification, stakeholder alignment, testable acceptance criteria, or traceability from PRD to tests.
---

# SDLC BDD Specifications

## Purpose

Use concrete examples to close ambiguity between business, product, design, engineering, and QA.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Identify actors, goals, rules, examples, counterexamples, and open questions.
2. Use example mapping to separate rules, scenarios, edge cases, and unknowns.
3. Write scenarios in business language, not UI implementation language unless UI behavior is the point.
4. Connect every scenario to acceptance tests and requirements.
5. Keep scenarios small, deterministic, and valuable as living documentation.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/product/bdd/, docs/quality/acceptance-tests.md, docs/product/requirements-traceability.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not generate code from a story whose critical examples and edge cases are still unknown.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
