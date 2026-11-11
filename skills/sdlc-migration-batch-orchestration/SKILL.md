---
name: sdlc-migration-batch-orchestration
description: Run migration as vertical batches cut from the frozen registry, with measured exit criteria and an independent verification gate per batch. Use for incremental rewrites or replatforming.
---

# SDLC Migration Batch Orchestration

## Purpose

Keep large migrations honest: progress is counted on the registry, a batch closes only on proof, and drift is caught early.

## Workflow

1. Phase 0, registry: `sdlc-legacy-inventory-registry` for every source; exit when `scripts/sdlc_registry.py check` is clean and the business reviewed abandoned and deferred lines.
2. Phase 1, batching: assign every registry line to a batch; a batch is a deliverable vertical slice (persistence, port, adapter, route, contract, client, screen, tests). Estimate write actions by field count.
3. Phase 2, reverse engineering of the batch: `sdlc-legacy-reverse-engineering`; exit when R1 rules are confirmed.
4. Phase 3, contracts and characterization: define interface contracts, then `sdlc-characterization-testing` against the real legacy; exit when oracles run.
5. Phase 4, build: implement the slice test-first in an isolated worktree, claiming lines with proof via `scripts/sdlc_registry.py claim`.
6. Phase 5, close: run `sdlc-reachability-anti-simulation`, then an independent verifier runs `sdlc-independent-verification`; only the verifier moves lines to PORTED.
7. Phase 6, capitalize: batch report, anomalies, lessons into the retrospective, and adjust remaining batches.
8. Report progress from `python scripts/sdlc_registry.py report`, never from what was written; refuse a batch close with unresolved refusals.

## Outputs

- Primary artifacts: Batch plan, per-batch audit and report, registry movement, lessons log.

## Guardrails

- A phase without its measured exit criterion is not finished.
- The implementer never verifies their own lines.
- Do not report percent complete from code volume or test count; use the registry denominator.
- Human approval remains required for dependency additions, destructive migrations, and production cutover.

## Handoff

`sdlc-data-migration-reconciliation` for data batches, `sdlc-cutover-rollback` when batches reach go-live.

## Provenance

Original to this suite; informed by registry-driven, verifier-gated migration programs. Provenance is tracked in `docs/references/method-sources.md`.
