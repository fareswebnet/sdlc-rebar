---
name: sdlc-task-breakdown
description: Turn an approved spec, plan, contracts, and BDD scenarios into a dependency-ordered task list grouped by independently deliverable user story, with exact file paths, parallelization markers, test-first ordering, and checkpoints. Use after planning and before coding, or when an agent needs a task list it can execute without further interpretation.
---

# SDLC Task Breakdown

## Purpose

Make the plan executable: each task is small, unambiguous, traceable to a requirement, and runnable by an agent or human without guessing.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Load the plan, spec, data model, contracts, and BDD scenarios; confirm user stories carry priorities (P1, P2, P3).
2. Create phases: Setup, Foundations (blocking prerequisites), then one phase per user story in priority order, then Polish and cross-cutting work.
3. Within a story, order tests first, then models, services, interfaces, and integration. Tests must exist and fail before the code that satisfies them.
4. Write each task as `- [ ] T### [P?] [US#] Action with exact/file/path`. Mark `[P]` only when files and dependencies are disjoint from sibling tasks.
5. Add a checkpoint after each story: the slice must be demonstrable and testable on its own, and a story must never require a later story.
6. State the dependency graph and the MVP cut (usually story P1 only), plus validation commands per checkpoint.
7. Cross-check: every requirement, scenario, and contract maps to at least one task, and every task maps back to one of them.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/engineering/tasks.md` (see `templates/docs/engineering/tasks.md`), dependency graph, MVP scope, parallel groups.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- No vague tasks such as `implement backend`; name the file and the observable result.
- Do not mark tasks parallel when they edit the same file or depend on unfinished outputs.
- Do not generate tests the spec did not ask for in Lean mode; in Standard and above, tests follow risk.
- Keep tasks small enough to review in one diff (target one commit).

## Handoff

`sdlc-cross-artifact-analysis` and `sdlc-traceability-ledger` before execution; `sdlc-tasks-to-issues` when tracked externally.

## Source Guidance

Adapted idea, extended beyond the source, not copied text: speckit-tasks (story-grouped, `[P]` markers, checkpoints) and superpowers writing-plans (bite-sized, exact paths, no unexplained steps). Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
