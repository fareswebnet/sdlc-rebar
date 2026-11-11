# legacy-migration

- Use for rewrites, replatforming, framework upgrades, or modernization of a system with thin documentation.
- Start with `sdlc-legacy-inventory-registry`; run `harnesses/legacy-migration.yaml`.
- Raise depth for `sdlc-characterization-testing`, `sdlc-independent-verification`, `sdlc-data-migration-reconciliation`, and `sdlc-cutover-rollback`.
- Measure progress only with `python scripts/sdlc_registry.py report`; classify R1 (money, security, compliance), R2 (workflows), R3 (presentation) and scale proof to risk.
- Reject legacy defects in the target by default and record each deliberate reproduction.
