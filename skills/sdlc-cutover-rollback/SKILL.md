---
name: sdlc-cutover-rollback
description: Plan cutover from legacy to target with a strangler or parallel-run strategy, rehearsed switch and rollback, reliability measurements, and an explicit go/no-go owned by a named person. Use when moving traffic or users from an old system to a new one, or when releasing a high-risk migration batch.
---

# SDLC Cutover And Rollback

## Purpose

Make the switch reversible, rehearsed, and measured, so go-live is a decision, not a leap.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Choose the strategy: strangler by route or tenant, parallel run with comparison, or big-bang with justification; define the unit of switch and its blast radius.
2. For parallel runs, send the same traffic to both systems, compare outputs automatically within the contract tolerances, and review every divergence before widening.
3. Prepare switches: feature flags or routing rules, data sync direction, freeze windows, and communication plan.
4. Rehearse the cutover and rollback end to end on production-shaped data; time each step and record the point of no return.
5. Set exit gates from `sdlc-observability-reliability`: error rate, latency budget (`sdlc-performance-budgets`), reconciliation clean, support readiness.
6. Execute in stages (internal, pilot tenants, wider), checking gates between stages; rollback on a gate breach without debate.
7. Hold go/no-go with a named owner, and keep the legacy read-only until the retention decision is recorded.
8. After cutover, monitor a defined period, then decommission the old system only with sign-off and archived data.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Cutover plan, rehearsal log, go/no-go record, post-cutover monitoring report.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Production deployment and customer communication need explicit human approval.
- A success of tests does not trigger cutover; the delivery authorization does.
- Do not decommission before data retention and audit needs are met.
- Any step not rehearsed is unproven; say so in the go/no-go.

## Handoff

`sdlc-release-production-readiness` for general release gates, `sdlc-incident-support-feedback` for the post-cutover loop.

## Source Guidance

Original to this suite; informed by strangler fig and parallel-run migration practice. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
