---
name: sdlc-data-migration-reconciliation
description: Plan and prove data migration or merge: source-to-target mapping, transformation rules, deduplication and identity resolution, ownership, dry runs, reconciliation counts and checksums, and rehearsed rollback. Use when moving data between systems, merging two datasets, changing schemas with live data, or preparing a cutover.
disable-model-invocation: true
---

# SDLC Data Migration Reconciliation

## Purpose

Show that every record that mattered arrived, correctly, once, with a way back.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Map source to target field by field with type, nullability, defaults, and transformation; list reference data and their mapping first.
2. Resolve identity: choose keys, survivorship rules for duplicates, and the owner of conflicts; for merges keep a crosswalk from old to new ids.
3. Write transformations as testable functions and cover each with golden samples including nulls, bad encodings, and boundary values.
4. Run repeated dry runs on production-shaped data; measure duration, failure classes, and quarantine rejected rows with reasons rather than dropping them.
5. Reconcile after each run: row counts per entity, sums of monetary fields at contractual rounding, hash or checksum samples, referential integrity, and business invariants.
6. Make migration idempotent and resumable; verify replay and partial-failure behavior.
7. Rehearse rollback and the reverse path before cutover; record the point of no return explicitly.
8. Protect data: masked data outside production, access controls on extracts, retention and deletion for temporary copies.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/migration/data-mapping.md`, reconciliation reports, quarantine log, rollback rehearsal record.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- No destructive migration without human approval and a verified backup.
- Never log or store personal or financial data in dry-run reports beyond what is needed.
- Counts alone are not reconciliation; compare values and invariants.
- A rejected row is a finding, not noise.

## Handoff

`sdlc-cutover-rollback` for go-live, `sdlc-data-database-architecture` for target schema design.

## Source Guidance

Original to this suite; informed by data migration and reconciliation practice. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
