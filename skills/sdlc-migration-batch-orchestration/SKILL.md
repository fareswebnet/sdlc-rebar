---
name: sdlc-migration-batch-orchestration
description: Plan and run a migration or modernization as vertical batches cut from the frozen registry, with a measured exit criterion per phase, an independent verification gate at each batch close, and capitalization of lessons. Use when a legacy system is rewritten or replatformed incrementally, and when an agent system must keep honest progress numbers.
---

# SDLC Migration Batch Orchestration

## Purpose

Keep large migrations honest: progress is counted on the registry, a batch closes only on proof, and drift is caught early.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Phase 0, registry: `sdlc-legacy-inventory-registry` for every source; exit when `scripts/sdlc_registry.py check` is clean and the business reviewed abandoned and deferred lines.
2. Phase 1, batching: assign every registry line to a batch; a batch is a deliverable vertical slice (persistence, port, adapter, route, contract, client, screen, tests). Estimate write actions by field count.
3. Phase 2, reverse engineering of the batch: `sdlc-legacy-reverse-engineering`; exit when R1 rules are confirmed.
4. Phase 3, contracts and characterization: define interface contracts, then `sdlc-characterization-testing` against the real legacy; exit when oracles run.
5. Phase 4, build: implement the slice test-first in an isolated worktree, claiming lines with proof via `scripts/sdlc_registry.py claim`.
6. Phase 5, close: run `sdlc-reachability-anti-simulation`, then an independent verifier runs `sdlc-independent-verification`; only the verifier moves lines to PORTED.
7. Phase 6, capitalize: batch report, anomalies, lessons into the retrospective, and adjust remaining batches.
8. Report progress from `python scripts/sdlc_registry.py report`, never from what was written; refuse a batch close with unresolved refusals.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Batch plan, per-batch audit and report, registry movement, lessons log.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- A phase without its measured exit criterion is not finished.
- The implementer never verifies their own lines.
- Do not report percent complete from code volume or test count; use the registry denominator.
- Human approval remains required for dependency additions, destructive migrations, and production cutover.

## Handoff

`sdlc-data-migration-reconciliation` for data batches, `sdlc-cutover-rollback` when batches reach go-live.

## Source Guidance

Original to this suite; informed by registry-driven, verifier-gated migration programs. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
