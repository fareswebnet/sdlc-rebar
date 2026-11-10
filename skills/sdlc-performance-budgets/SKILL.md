---
name: sdlc-performance-budgets
description: Define performance budgets (latency percentiles, throughput, payload and bundle size, memory, startup, query counts, cost per request) tied to user journeys and SLOs, measure them in CI and production, and treat a breach as a failing gate. Use when designing user-facing or high-volume features, before release, or when performance regressions keep slipping through.
---

# SDLC Performance Budgets

## Purpose

Turn 'it should be fast' into numbers with owners, tests, and consequences.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Pick the journeys that matter and the user-visible metrics for each (for web: LCP, INP, CLS; for APIs: p50, p95, p99 latency, error rate; for mobile: startup and frame time; for batch: duration and throughput).
2. Set a budget per metric from the SLO and the competition or baseline, with an explicit environment and data volume; add resource budgets (bundle size, queries per request, memory, cost per 1,000 operations).
3. Measure the baseline before changing anything, on production-shaped data.
4. Automate: load and benchmark tests in CI for hot paths, bundle-size and query-count checks per PR, and synthetic checks in production; store results over time.
5. Break down the budget across tiers (client, edge, service, database) so each team owns a share.
6. On breach, fail the gate or require a recorded waiver with owner and expiry; investigate with profiling before optimizing.
7. Review budgets each release and after incidents; tighten what is comfortably met.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/operations/performance-budgets.md`, CI performance checks, dashboards, waiver log.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not optimize without a measurement and a budget.
- Averages hide tail latency; budget percentiles.
- Budgets measured on toy data are fiction; state the data volume.
- A waiver without an expiry becomes the new budget.

## Handoff

`$sdlc-performance-scalability-cost` for capacity and cost, `$sdlc-observability-reliability` for production SLOs.

## Source Guidance

Original to this suite; informed by web performance budgets and SRE latency objectives. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
