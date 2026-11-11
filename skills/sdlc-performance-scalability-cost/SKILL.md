---
name: sdlc-performance-scalability-cost
description: Review scalability, capacity, and cloud or LLM cost: FinOps, unit economics, bottlenecks, caching. Use when designing high-volume features, optimizing production, or forecasting infrastructure cost.
---

# SDLC Performance Scalability Cost

## Purpose

Treat cost and scalability as first-class architecture constraints.

## Workflow

1. Define workload model, expected growth, latency, throughput, availability, and cost targets.
2. Identify bottlenecks in app, DB, cache, queue, network, storage, LLM/API calls, and observability.
3. Estimate unit cost by user, tenant, transaction, document, workflow, or AI request.
4. Compare trade-offs between performance, reliability, complexity, and spend.
5. Add budgets, quotas, alerts, and optimization opportunities.

## Outputs

- Primary artifacts: `docs/operations/performance-review.md, docs/operations/cost-model.md, docs/architecture/scaling-plan.md`.

## Guardrails

- Do not optimize blindly; tie work to measured bottlenecks, forecast risk, or unit economics.
