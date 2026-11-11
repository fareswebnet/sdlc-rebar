---
name: sdlc-tasks-to-issues
description: Convert an approved task list into dependency-linked issues in GitHub, GitLab, Jira, or Linear, and keep status synchronized with the repo task file, after explicit human approval. Use when a team tracks work outside the repo, when tasks must be assigned across people or agents, or when progress needs to be visible to stakeholders.
disable-model-invocation: true
---

# SDLC Tasks To Issues

## Purpose

Keep the repo task list and the tracker consistent without creating noise or duplicate work.

## Workflow

1. Confirm `docs/engineering/tasks.md` passed `sdlc-cross-artifact-analysis` and `python scripts/sdlc_trace.py`; do not sync a plan with HIGH findings.
2. Verify the remote: show the target repository or project and wait for approval before creating anything.
3. Create one epic per feature and one issue per user story; keep individual tasks as checklist items unless they need separate owners.
4. Put in each issue: goal, acceptance scenarios, requirement ids, task ids, dependencies, validation command, and the MVP flag.
5. Link blockers and parallel groups; label by priority and story id.
6. Record issue numbers back into the task file so the mapping is two-way, and detect duplicates before creating new ones.
7. On later runs, reconcile status: closed issues with open tasks, and done tasks with open issues, are reported rather than silently changed.

## Outputs

- Primary artifacts: Epic and issues with links, mapping table in `docs/engineering/tasks.md`, reconciliation report.

## Guardrails

- Creating issues is an external write: require explicit approval for the exact remote and scope.
- Never create issues in a repository that does not match the local remote without confirmation.
- Do not paste secrets or customer data into issue bodies.
- No bulk edits of existing issues without a diff and approval.

## Runtime Fallbacks

Without tracker access, output each issue as Markdown (title, body, labels, dependencies) for a human to create, then record the real issue numbers they return; never invent identifiers. See `docs/references/runtime-capabilities.md`.

## Handoff

`sdlc-subagent-driven-execution` to run the tasks, `sdlc-delivery-roadmap-backlog` for prioritization.

## Provenance

Original to this suite; informed by Spec Kit taskstoissues, extended with reconciliation, dependency links, and a two-way mapping. Provenance is tracked in `docs/references/method-sources.md`.
