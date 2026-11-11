---
name: sdlc-cross-artifact-analysis
description: Run a strictly read-only consistency and coverage audit across the constitution, spec, plan, BDD, and tasks, detecting duplication, ambiguity, underspecification, contradictions, uncovered requirements, and orphan tasks, with severity and a remediation list. Use after task breakdown and before implementation, or before a release gate.
---

# SDLC Cross-Artifact Analysis

## Purpose

Catch the cheap-to-fix problems between documents before they become expensive code.

## Workflow

1. Load only the necessary parts of each artifact; build an inventory of requirements, scenarios, entities, contracts, and tasks with stable ids.
2. Detect: duplicate requirements, vague adjectives without metrics, unresolved markers, conflicting terms, requirements with no task, tasks with no requirement, ordering contradictions, and constitution violations.
3. Assign severity: CRITICAL (violates a MUST principle or blocks baseline functionality), HIGH, MEDIUM, LOW.
4. Produce a findings table (id, category, location, summary, recommendation), a coverage matrix (requirement to tasks), and metrics (coverage %, ambiguity count, critical count).
5. Offer remediation as a proposed edit list; apply changes only after explicit user approval.
6. Cap the report at about 50 findings and aggregate the overflow.

## Outputs

- Primary artifacts: Analysis report (see `templates/docs/governance/analysis-report.md`), coverage matrix, next-action recommendation.

## Guardrails

- Strictly read-only until the user approves edits.
- Constitution conflicts are always CRITICAL; fix the artifact, never quietly dilute the principle.
- Do not hallucinate missing sections; report absence as a finding.
- Findings must be deterministic and reproducible: same inputs, same ids.

## Handoff

`sdlc-spec-clarification` or `sdlc-task-breakdown` to fix findings; `sdlc-traceability-ledger` for the script-checked matrix.

## Provenance

Adapted idea, extended beyond the source, not copied text: speckit-analyze (read-only, severity-ranked, coverage matrix). Provenance is tracked in `docs/references/method-sources.md`.
