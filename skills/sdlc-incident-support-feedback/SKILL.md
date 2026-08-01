---
name: sdlc-incident-support-feedback
description: Handle incident response, postmortems, support ticket normalization, customer feedback triage, bug reproduction, customer impact prioritization, and feedback-to-roadmap loops. Use during incidents, after production issues, or when support/customer success signals should improve product quality.
---

# SDLC Incident Support Feedback

## Purpose

Convert production and customer pain into learning and durable improvements.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Triage severity, customer impact, scope, timeline, and immediate mitigation.
2. Normalize bug reports into reproducible expected/actual behavior.
3. Write postmortems focused on contributing factors, detection, response, and prevention.
4. Convert support patterns into backlog, docs, UX, reliability, or product analytics work.
5. Track owners and follow-up actions until closed.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/operations/incidents/, docs/operations/postmortems/, docs/support/feedback-triage.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not stop at root cause labels; identify system changes that reduce recurrence.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
