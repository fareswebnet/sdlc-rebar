---
name: sdlc-observability-reliability
description: Design observability, reliability, SLIs, SLOs, error budgets, logs, metrics, traces, dashboards, alerts, runbooks, capacity signals, and production health checks. Use when preparing production, diagnosing reliability gaps, setting monitoring, or improving operational maturity.
---

# SDLC Observability Reliability

## Purpose

Help teams understand production behavior from user and business impact, not only infrastructure metrics.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Identify critical user journeys, services, dependencies, and failure modes.
2. Define SLIs and SLOs from user-visible behavior and business expectations.
3. Specify logs, metrics, traces, dashboards, alerts, and runbooks.
4. Tune alerting so pages require action and tickets represent deferred work.
5. Feed incidents, support signals, and DORA metrics into continuous improvement.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/operations/observability.md, docs/operations/slo.md, docs/operations/runbooks/`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not alert humans for signals that have no expected action.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
