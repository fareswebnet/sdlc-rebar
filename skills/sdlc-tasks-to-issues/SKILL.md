---
name: sdlc-tasks-to-issues
description: Convert an approved task list into dependency-linked issues in GitHub, GitLab, Jira, or Linear, and keep status synchronized with the repo task file, after explicit human approval. Use when a team tracks work outside the repo, when tasks must be assigned across people or agents, or when progress needs to be visible to stakeholders.
---

# SDLC Tasks To Issues

## Purpose

Keep the repo task list and the tracker consistent without creating noise or duplicate work.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Confirm `docs/engineering/tasks.md` passed `$sdlc-cross-artifact-analysis` and `python scripts/sdlc_trace.py`; do not sync a plan with HIGH findings.
2. Verify the remote: show the target repository or project and wait for approval before creating anything.
3. Create one epic per feature and one issue per user story; keep individual tasks as checklist items unless they need separate owners.
4. Put in each issue: goal, acceptance scenarios, requirement ids, task ids, dependencies, validation command, and the MVP flag.
5. Link blockers and parallel groups; label by priority and story id.
6. Record issue numbers back into the task file so the mapping is two-way, and detect duplicates before creating new ones.
7. On later runs, reconcile status: closed issues with open tasks, and done tasks with open issues, are reported rather than silently changed.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Epic and issues with links, mapping table in `docs/engineering/tasks.md`, reconciliation report.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Creating issues is an external write: require explicit approval for the exact remote and scope.
- Never create issues in a repository that does not match the local remote without confirmation.
- Do not paste secrets or customer data into issue bodies.
- No bulk edits of existing issues without a diff and approval.

## Handoff

`$sdlc-subagent-driven-execution` to run the tasks, `$sdlc-delivery-roadmap-backlog` for prioritization.

## Source Guidance

Original to this suite; informed by Spec Kit taskstoissues, extended with reconciliation, dependency links, and a two-way mapping. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
