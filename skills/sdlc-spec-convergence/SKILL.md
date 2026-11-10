---
name: sdlc-spec-convergence
description: Compare the current codebase to the spec, plan, and task list to find what was actually built, what is partial, and what remains, then append the missing work as new tasks. Use after an implementation pass, after an interrupted agent run, or when a feature branch has drifted from its spec.
---

# SDLC Spec Convergence

## Purpose

Close the loop between intent and code so remaining work is explicit instead of assumed.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Read the spec, plan, tasks, and BDD scenarios; list each requirement with its expected observable behavior.
2. Inspect the repository and tests for evidence per requirement: implemented and tested, implemented only, partial, missing, or diverged from the spec.
3. Run the existing test suite and acceptance scenarios; treat failing or absent tests as evidence, not assumptions.
4. Classify drift: code ahead of spec (propose spec update), code behind spec (new task), or deliberate deviation (record a decision).
5. Append new tasks to the task list using the same id and format rules as `$sdlc-task-breakdown`; never renumber or delete completed tasks.
6. Summarize the delta: done, remaining, drifted, risky, and the next safe step.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Updated `docs/engineering/tasks.md` with new tasks, drift notes, decision-log entries for deviations.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Evidence must be a file, test, or command output; do not mark done on the basis of a plausible-looking diff.
- Do not rewrite the spec to match the code without a recorded decision.
- Do not implement the new tasks in the same step; hand them to execution.
- Stay within the feature scope; list unrelated findings separately.

## Handoff

`$sdlc-subagent-driven-execution` to build appended tasks; `$sdlc-delivery-retrospective` for recurring drift.

## Source Guidance

Adapted idea, extended beyond the source, not copied text: speckit-converge (assess build against spec, append unbuilt work). Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
