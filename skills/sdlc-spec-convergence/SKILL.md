---
name: sdlc-spec-convergence
description: Compare code to spec, plan, and tasks to find what is built, partial, or missing, and append missing work as tasks. Use after an implementation pass, an interrupted agent run, or spec drift.
---

# SDLC Spec Convergence

## Purpose

Close the loop between intent and code so remaining work is explicit instead of assumed.

## Workflow

1. Read the spec, plan, tasks, and BDD scenarios; list each requirement with its expected observable behavior.
2. Inspect the repository and tests for evidence per requirement: implemented and tested, implemented only, partial, missing, or diverged from the spec.
3. Run the existing test suite and acceptance scenarios; treat failing or absent tests as evidence, not assumptions.
4. Classify drift: code ahead of spec (propose spec update), code behind spec (new task), or deliberate deviation (record a decision).
5. Append new tasks to the task list using the same id and format rules as `sdlc-task-breakdown`; never renumber or delete completed tasks.
6. Summarize the delta: done, remaining, drifted, risky, and the next safe step.

## Outputs

- Primary artifacts: Updated `docs/engineering/tasks.md` with new tasks, drift notes, decision-log entries for deviations.

## Guardrails

- Evidence must be a file, test, or command output; do not mark done on the basis of a plausible-looking diff.
- Do not rewrite the spec to match the code without a recorded decision.
- Do not implement the new tasks in the same step; hand them to execution.
- Stay within the feature scope; list unrelated findings separately.

## Handoff

`sdlc-subagent-driven-execution` to build appended tasks; `sdlc-delivery-retrospective` for recurring drift.

## Provenance

Adapted idea, extended beyond the source, not copied text: speckit-converge (assess build against spec, append unbuilt work). Provenance is tracked in `docs/references/method-sources.md`.
