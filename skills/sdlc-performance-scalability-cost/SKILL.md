---
name: sdlc-performance-scalability-cost
description: Review performance, scalability, capacity, cloud cost, FinOps, unit economics, LLM/API costs, database bottlenecks, caching, queues, storage, observability cost, and architecture trade-offs. Use when designing high-volume features, optimizing production, forecasting infrastructure cost, or preparing investor/enterprise diligence.
---

# SDLC Performance Scalability Cost

## Purpose

Treat cost and scalability as first-class architecture constraints.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Define workload model, expected growth, latency, throughput, availability, and cost targets.
2. Identify bottlenecks in app, DB, cache, queue, network, storage, LLM/API calls, and observability.
3. Estimate unit cost by user, tenant, transaction, document, workflow, or AI request.
4. Compare trade-offs between performance, reliability, complexity, and spend.
5. Add budgets, quotas, alerts, and optimization opportunities.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/operations/performance-review.md, docs/operations/cost-model.md, docs/architecture/scaling-plan.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not optimize blindly; tie work to measured bottlenecks, forecast risk, or unit economics.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
