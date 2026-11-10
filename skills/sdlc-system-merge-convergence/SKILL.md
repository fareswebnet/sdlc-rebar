---
name: sdlc-system-merge-convergence
description: Merge two or more systems, codebases, or business estates into one target by inventorying each independently, classifying every rule as equivalent, parameterizable, additive, or contradictory, deciding data and contract ownership, and proving cumulative non-regression of every source. Use for acquisitions, platform consolidation, tenant merges, or integrating a second legacy source into an existing target.
---

# SDLC System Merge Convergence

## Purpose

Converge without silently losing either side: every source is inventoried alone, every rule is classified and proven, and the earlier sources stay green.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Inventory the incoming source independently with `sdlc-legacy-inventory-registry`, even when it resembles an earlier source; use one registry with a source column plus a cross-source matrix.
2. Extract its rules into a dedicated matrix (`RG-<SOURCE>-<NNN>`) before any implementation.
3. Cut convergence into end-to-end business slices (calculation core, documents, back-office workflow, mobile) rather than horizontal layers; reconcile the highest-risk core first.
4. Classify each rule pair: equivalent, parameterizable (one engine with configuration), additive (new capability), or contradictory (decision needed). An equivalence is a conclusion to prove on both sources; matching names are only a lead.
5. Name an owner for data, identifiers, contracts, and decisions. Resolve field mappings, duplicates, roles, and tenants before building cross-source features.
6. Prefer a policy or strategy for local variation; for different domains or lifecycles keep separate contexts with an anti-corruption layer. One target does not mean one shared table or one owner for all data.
7. Keep legacy disposition, convergence analysis, public proof, visa, and cutover state in separate columns; never copy a visa from one source to another.
8. Add the new source to the cumulative regression harness and rerun earlier sources' proven journeys; a regression reopens their lines.
9. Close through `sdlc-independent-verification` in a context distinct from the converger and prepare cutover with `sdlc-cutover-rollback`.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Cross-source registry and rule matrices, classification table, ownership decisions, cumulative regression results.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- A visa applies to one source only.
- Do not reproduce legacy defects or weaknesses; reject invalid input with standard error responses and record the improvement.
- Do not use a reimplementation as the proof of its own equivalence.
- Contradictions need a named decision owner; do not choose silently.

## Handoff

`sdlc-data-migration-reconciliation` for data, `sdlc-bounded-context-map` for ownership boundaries.

## Source Guidance

Original to this suite; informed by multi-source convergence in portfolio migrations. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
