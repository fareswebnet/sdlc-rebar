# Pipeline: Legacy Migration

Use when replacing or modernizing a legacy system incrementally, where progress must be measured against what existed.

## Outcome

A registry in which every line is closed by proof and independent visa, or by a signed decision, and a rehearsed cutover.

## Sequence

1. `legacy-analyst` freezes the registry for every source (`python scripts/sdlc_registry.py init`, then `check`).
2. `orchestrator` cuts vertical batches covering every line.
3. `legacy-analyst` extracts business rules for the batch.
4. `qa-test-engineer` builds oracles and the differential suite against the real legacy.
5. `fullstack-builder` implements the slice test-first and claims lines with proof.
6. `independent-verifier` samples, exercises, mutates, and grants or refuses visas.
7. `release-manager` rehearses cutover and rollback and holds go/no-go.
8. `orchestrator` capitalizes lessons and adjusts remaining batches.

## Gates

- Do not build on a source whose registry is not frozen and reviewed.
- Do not count progress except from `python scripts/sdlc_registry.py report`.
- Do not let an implementer visa their own lines; the tool refuses it.
- Do not cut over without a rehearsed rollback and a named go/no-go owner.

## Runtime Hints

- Run the verifier as a separate session, ideally a different model, with only the registry, repo, and skill.
- CI: run `sdlc_registry.py check` and the reachability ratchet on every PR.
