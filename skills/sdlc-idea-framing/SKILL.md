---
name: sdlc-idea-framing
description: Frame raw software, SaaS, fintech, AI, marketplace, internal-tool, or platform ideas into a clear problem, audience, value proposition, alternatives, assumptions, constraints, and no-go areas. Use before PRD, architecture, backlog, or MVP planning when the idea is still ambiguous.
---

# SDLC Idea Framing

## Purpose

Convert a vague idea into a testable product thesis.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. State the problem in plain language and identify who feels it.
2. Describe current alternatives, workaround behavior, and why now matters.
3. Separate user pain, business opportunity, technical possibility, and personal preference.
4. List assumptions that must be validated before building.
5. Define the smallest credible next proof point.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/product/vision.md, docs/product/assumptions.md, docs/product/problem-statement.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not move to solution design until the user, pain, current alternative, and falsifiable assumptions are named.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
