# sdlc-data-migration-reconciliation (compact)

When: Plan and prove data migration or merge: source-to-target mapping, transformation rules, deduplication and identity resolution, ownership, dry runs, reconciliation counts and checksums, and rehearsed rollback.

Goal: Show that every record that mattered arrived, correctly, once, with a way back.

Steps:
1. Map source to target field by field with type, nullability, defaults, and transformation; list reference data and their mapping…
2. Resolve identity: choose keys, survivorship rules for duplicates, and the owner of conflicts; for merges keep a crosswalk from…
3. Write transformations as testable functions and cover each with golden samples including nulls, bad encodings, and boundary…
4. Run repeated dry runs on production-shaped data; measure duration, failure classes, and quarantine rejected rows with reasons…
5. Reconcile after each run: row counts per entity, sums of monetary fields at contractual rounding, hash or checksum samples…
6. Make migration idempotent and resumable; verify replay and partial-failure behavior.
7. Rehearse rollback and the reverse path before cutover; record the point of no return explicitly.
8. Protect data: masked data outside production, access controls on extracts, retention and deletion for temporary copies.

Never:
- No destructive migration without human approval and a verified backup.
- Never log or store personal or financial data in dry-run reports beyond what is needed.
- Counts alone are not reconciliation; compare values and invariants.
- A rejected row is a finding, not noise.

Next: `sdlc-cutover-rollback` for go-live, `sdlc-data-database-architecture` for target schema design.
