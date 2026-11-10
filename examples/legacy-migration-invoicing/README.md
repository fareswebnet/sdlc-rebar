# Example: Legacy Migration, Invoicing Core

A small but complete run of the `harnesses/legacy-migration.yaml` flow on a fictional invoicing module, executable end to end:

```bash
python examples/legacy-migration-invoicing/run_example.py          # verify the whole flow
python examples/legacy-migration-invoicing/run_example.py --write  # refresh artifacts/
```

The script plays every role mechanically so the flow is reproducible. In a real migration the builder and the verifier are separate agents or people, and the verifier works in a fresh context.

## Layout

| Path | Role | Skill |
|---|---|---|
| `legacy/billing.py` | The real legacy, used as the oracle and never edited | `sdlc-characterization-testing` |
| `inventory.csv` | Script-style inventory of 7 things that existed | `sdlc-legacy-inventory-registry` |
| `docs/rules.md` | Business rules `RG-INV-*`, legacy defect decision | `sdlc-legacy-reverse-engineering` |
| `docs/batch-plan.md` | Vertical batches covering every line | `sdlc-migration-batch-orchestration` |
| `target/billing.py`, `target/routes.py` | Migrated module and its routes | `sdlc-test-driven-development` |
| `target/billing_first_attempt.py` | First attempt, kept to show the oracle catching it | `sdlc-characterization-testing` |
| `tests/` | Differential suite (boundaries plus seeded fuzz, exact equality) | `sdlc-characterization-testing` |
| `artifacts/registry.final.csv` | Registry after claims, visas, and decisions | `scripts/sdlc_registry.py` |
| `artifacts/batch-B1-audit.md` | Verifier report for batch B1 | `sdlc-independent-verification` |
| `artifacts/run-log.md` | What each step produced | all |

## What the run demonstrates

1. The registry fixes the denominator: 7 lines, each with a disposition.
2. The oracle catches a plausible first implementation: default rounding differs from the legacy half-up rule on 437 comparisons, starting with the 1000.10 boundary.
3. The final target matches the legacy exactly on boundaries and 2,000 seeded random cases per function.
4. People decide the non-code lines: one REPLACED with the replacement named, one ABANDONED with a business signer, one DEFERRED to batch B2.
5. The builder can claim lines but the tool refuses a self-granted visa.
6. The reachability ratchet is green, and a new unrouted function would fail it.
7. A mutation (discount 5% to 6%) makes 817 comparisons fail, so the proof is not vacuous.
8. Progress is reported on the denominator: 6 of 7 lines closed (85.7%), with 1 line honestly deferred.

## Scale notes

- This batch is tiny, so the sample rate is 100%. Real batches sample about 10% plus all priority-1 lines.
- Priority-1 lines would get two independent verifiers.
- A real run adds data reconciliation (`sdlc-data-migration-reconciliation`) and a rehearsed cutover (`sdlc-cutover-rollback`) before decommissioning the legacy.
