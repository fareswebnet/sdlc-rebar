# sdlc-cross-artifact-analysis (compact)

When: Run a read-only consistency audit across constitution, spec, plan, BDD, and tasks for contradictions, uncovered requirements, orphan tasks.

Goal: Catch the cheap-to-fix problems between documents before they become expensive code.

Steps:
1. Load only the necessary parts of each artifact; build an inventory of requirements, scenarios, entities, contracts, and tasks…
2. Detect: duplicate requirements, vague adjectives without metrics, unresolved markers, conflicting terms, requirements with no…
3. Assign severity: CRITICAL (violates a MUST principle or blocks baseline functionality), HIGH, MEDIUM, LOW.
4. Produce a findings table (id, category, location, summary, recommendation), a coverage matrix (requirement to tasks), and metrics…
5. Offer remediation as a proposed edit list; apply changes only after explicit user approval.
6. Cap the report at about 50 findings and aggregate the overflow.

Never:
- Strictly read-only until the user approves edits.
- Constitution conflicts are always CRITICAL; fix the artifact, never quietly dilute the principle.
- Do not hallucinate missing sections; report absence as a finding.
- Findings must be deterministic and reproducible: same inputs, same ids.

Next: `sdlc-spec-clarification` or `sdlc-task-breakdown` to fix findings; `sdlc-traceability-ledger` for the script-checked matrix.
