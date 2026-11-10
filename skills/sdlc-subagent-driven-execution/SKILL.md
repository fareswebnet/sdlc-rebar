---
name: sdlc-subagent-driven-execution
description: Execute a task list by dispatching a fresh subagent per task with exactly the context it needs, followed by a spec-compliance review and a code-quality review, and by running genuinely independent work in parallel. Use when tasks are mostly independent, when the plan is written, and when agent context isolation and review gates matter.
---

# SDLC Subagent-Driven Execution

## Purpose

Keep each agent focused and each change reviewed, so large plans execute reliably without context pollution.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Read the task list once; extract each task's full text, context, files, and validation commands, and create tracking items.
2. Group tasks by independence: tasks with disjoint files and no data dependency may run in parallel; others run sequentially.
3. Dispatch one implementer per task with a self-contained brief: goal, exact files, constraints, tests, and the expected report format. Do not hand over your whole session history.
4. Handle implementer status: DONE, DONE_WITH_CONCERNS (read the concerns), NEEDS_CONTEXT (supply it and retry), BLOCKED (change context, model, or task size, or escalate).
5. After each task run two reviews in order: spec compliance (nothing missing, nothing extra), then code quality. Loop with the implementer until both approve.
6. Choose the lightest sufficient model for each role; reserve stronger models for integration, design, and review of risky tasks.
7. Verify the integrated result with `$sdlc-verification-before-completion`, then finish the branch via `$sdlc-branch-worktree-lifecycle`.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Per-task reports, review verdicts, integrated diff, final verification evidence.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Never run two implementers that edit the same files at once.
- Do not skip either review stage or accept `close enough` on spec compliance.
- Subagents must not inherit unrelated context; construct their input deliberately.
- Human gates from the harness still apply: dependencies, migrations, secrets, and deployments need approval.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| Spec review passed, skip quality review | Both reviews are required, in order. |
| Run these in parallel, they're related | If they touch the same files they are not independent. |

## Handoff

`$sdlc-agent-context-engineering` for briefs; `$sdlc-branch-worktree-lifecycle` and `$sdlc-spec-convergence` after the run.

## Source Guidance

Adapted idea, extended beyond the source, not copied text: superpowers subagent-driven-development, dispatching-parallel-agents, executing-plans. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
