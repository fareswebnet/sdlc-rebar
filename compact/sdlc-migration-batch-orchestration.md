# sdlc-migration-batch-orchestration (compact)

When: Plan and run a migration or modernization as vertical batches cut from the frozen registry, with a measured exit criterion per phase, an independent verification gate at each batch close, and capitalization of lessons.

Goal: Keep large migrations honest: progress is counted on the registry, a batch closes only on proof, and drift is caught early.

Steps:
1. Phase 0, registry: `sdlc-legacy-inventory-registry` for every source; exit when `scripts/sdlc_registry.py check` is clean and the…
2. Phase 1, batching: assign every registry line to a batch; a batch is a deliverable vertical slice (persistence, port, adapter…
3. Phase 2, reverse engineering of the batch: `sdlc-legacy-reverse-engineering`; exit when R1 rules are confirmed.
4. Phase 3, contracts and characterization: define interface contracts, then `sdlc-characterization-testing` against the real…
5. Phase 4, build: implement the slice test-first in an isolated worktree, claiming lines with proof via `scripts/sdlc_registry.py…
6. Phase 5, close: run `sdlc-reachability-anti-simulation`, then an independent verifier runs `sdlc-independent-verification`; only…
7. Phase 6, capitalize: batch report, anomalies, lessons into the retrospective, and adjust remaining batches.
8. Report progress from `python scripts/sdlc_registry.py report`, never from what was written; refuse a batch close with unresolved…

Never:
- A phase without its measured exit criterion is not finished.
- The implementer never verifies their own lines.
- Do not report percent complete from code volume or test count; use the registry denominator.
- Human approval remains required for dependency additions, destructive migrations, and production cutover.

Next: `sdlc-data-migration-reconciliation` for data batches, `sdlc-cutover-rollback` when batches reach go-live.
