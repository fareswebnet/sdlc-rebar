---
name: sdlc-ai-assisted-development
description: Plan and govern AI-assisted software development with context engineering, task decomposition, agent roles, coding guardrails, review loops, traceability from spec to code, and output evaluation. Use when coding with agents, creating agent workflows, splitting work across agents, or preventing AI-generated code from drifting from specs.
---

# SDLC AI Assisted Development

## Purpose

Use AI coding agents as supervised engineering workflows, not free-form generators.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Prepare the minimum useful context: repo conventions, specs, architecture, tests, constraints, and risks.
2. Decompose work into bounded tasks with expected artifacts and validation commands.
3. Assign agent roles only when independent perspectives add value.
4. Require spec-to-code traceability, tests, review, and rollback awareness.
5. Evaluate outputs for correctness, maintainability, security, UX, and scope control.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/engineering/ai-development-plan.md, docs/product/requirements-traceability.md, docs/quality/validation-plan.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not allow AI-generated changes that invent APIs, ignore local patterns, skip tests, or refactor outside scope.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
