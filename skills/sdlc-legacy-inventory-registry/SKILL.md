---
name: sdlc-legacy-inventory-registry
description: Produce a frozen script-generated registry of everything callable or visible in a legacy system, one disposition per line. Use before any target code in a migration, rewrite, or merge.
---

# SDLC Legacy Inventory Registry

## Purpose

Give the migration a denominator: a registry nobody can quietly shrink, where 100 percent means 100 percent of the old system.

## Workflow

1. Inventory each source repository with a script or the framework's own route and schema listing; never replace the inventory with a free-form reading. If no extractor exists for the technology, build one with a test before starting.
2. Enumerate by kind: ACTION, SCREEN, ENTITY, TABLE, COMMAND, JOB, OUTBOUND_CALL (the contract the target must serve), and RULE where rules are extracted.
3. Cross-check counts against the framework's own output (route list, ORM metadata, schema dump); explain or fix every gap before freezing.
4. Break write operations into fields: for every create or update, list the form or entity fields and constraints in the line's note or an attached field file. The denominator of a write is its field list.
5. Inventory reference data (lookup tables behind every choice list), implicit constraints (uniqueness, scoping by role or tenant), and homonyms (same action name in two repositories gets one line each).
6. Load the result with `python scripts/sdlc_registry.py init <registry.csv> <inventory.csv>`; the tool merges without losing decisions and marks vanished lines instead of deleting them.
7. Assign each line a disposition: OPEN, TO_VERIFY, PORTED (proof plus independent visa), REPLACED (replacement named and existing), ABANDONED (written justification and business signer), DEFERRED (named batch). Run `python scripts/sdlc_registry.py check`.
8. Have the business owner read every ABANDONED and DEFERRED line before the registry is frozen.

## Outputs

- Primary artifacts: `docs/migration/registry.csv`, per-repository inventory files, field files for write actions, signed list of abandoned and deferred lines.

## Guardrails

- No target work on a repository until its registry exists, is frozen, and was reviewed.
- Never delete a registry line; a line that disappears from a later inventory is marked, not erased.
- Generated and vendored folders must be ignored by the extractor, but check that no business logic hides inside them.
- Technical fragments (partial templates, AJAX snippets) may be REPLACED up front, but only with the replacement named.

## Handoff

`sdlc-migration-batch-orchestration` to cut batches, `sdlc-legacy-reverse-engineering` to extract rules.

## Provenance

Original to this suite; informed by the frozen-denominator discipline of production migration programs. Provenance is tracked in `docs/references/method-sources.md`.
