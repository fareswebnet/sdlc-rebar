---
name: sdlc-observability-reliability
description: Design observability and reliability: SLIs, SLOs, error budgets, logs, metrics, traces, alerts, runbooks. Use when preparing production, diagnosing reliability gaps, or setting up monitoring.
---

# SDLC Observability Reliability

## Purpose

Help teams understand production behavior from user and business impact, not only infrastructure metrics.

## Workflow

1. Identify critical user journeys, services, dependencies, and failure modes.
2. Define SLIs and SLOs from user-visible behavior and business expectations.
3. Specify logs, metrics, traces, dashboards, alerts, and runbooks.
4. Tune alerting so pages require action and tickets represent deferred work.
5. Feed incidents, support signals, and DORA metrics into continuous improvement.

## Outputs

- Primary artifacts: `docs/operations/observability.md, docs/operations/slo.md, docs/operations/runbooks/`.

## Guardrails

- Do not alert humans for signals that have no expected action.
