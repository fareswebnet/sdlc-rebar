---
name: sdlc-code-review-quality-gate
description: Perform code review and quality gates focused on correctness, maintainability, architecture boundaries, tests, security, performance, UX impact, migrations, observability, and release risk. Use before merge, before release, after AI-generated code, or when auditing a change set.
---

# SDLC Code Review Quality Gate

## Purpose

Find defects and risk before they reach users.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Review the diff against requirements, BDD scenarios, architecture decisions, and local code patterns.
2. Prioritize bugs, regressions, missing tests, security issues, and release blockers.
3. Check maintainability, coupling, naming, error handling, logging, and migration safety.
4. Separate blocking findings from improvements and stylistic preferences.
5. Require validation evidence or clearly state residual risk.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `review findings, merge gate decision, residual risk notes`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not approve code whose behavior cannot be connected to a spec or tested expectation.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
