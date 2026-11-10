---
name: sdlc-cross-artifact-analysis
description: Run a strictly read-only consistency and coverage audit across the constitution, spec, plan, BDD, and tasks, detecting duplication, ambiguity, underspecification, contradictions, uncovered requirements, and orphan tasks, with severity and a remediation list. Use after task breakdown and before implementation, or before a release gate.
---

# SDLC Cross-Artifact Analysis

## Purpose

Catch the cheap-to-fix problems between documents before they become expensive code.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Load only the necessary parts of each artifact; build an inventory of requirements, scenarios, entities, contracts, and tasks with stable ids.
2. Detect: duplicate requirements, vague adjectives without metrics, unresolved markers, conflicting terms, requirements with no task, tasks with no requirement, ordering contradictions, and constitution violations.
3. Assign severity: CRITICAL (violates a MUST principle or blocks baseline functionality), HIGH, MEDIUM, LOW.
4. Produce a findings table (id, category, location, summary, recommendation), a coverage matrix (requirement to tasks), and metrics (coverage %, ambiguity count, critical count).
5. Offer remediation as a proposed edit list; apply changes only after explicit user approval.
6. Cap the report at about 50 findings and aggregate the overflow.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Analysis report (see `templates/docs/governance/analysis-report.md`), coverage matrix, next-action recommendation.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Strictly read-only until the user approves edits.
- Constitution conflicts are always CRITICAL; fix the artifact, never quietly dilute the principle.
- Do not hallucinate missing sections; report absence as a finding.
- Findings must be deterministic and reproducible: same inputs, same ids.

## Handoff

`$sdlc-spec-clarification` or `$sdlc-task-breakdown` to fix findings; `$sdlc-traceability-ledger` for the script-checked matrix.

## Source Guidance

Adapted idea, extended beyond the source, not copied text: speckit-analyze (read-only, severity-ranked, coverage matrix). Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
