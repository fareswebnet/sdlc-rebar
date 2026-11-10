# Pipeline: Spec-Driven Delivery

Use when a feature needs strong traceability from intent to proof, for example regulated flows, multi-agent builds, or work that will be audited.

## Outcome

A branch or PR where each requirement id maps to a scenario, a task, a test, and evidence, with drift and lessons recorded.

## Sequence

1. `orchestrator` sets principles and the agent context (`sdlc-project-constitution`, `sdlc-agent-context-engineering`).
2. `product-strategist` runs the design gate and clarification.
3. `qa-test-engineer` checks requirement quality and tags BDD scenarios with ids.
4. `solution-architect` plans, breaks down tasks, and runs `python scripts/sdlc_trace.py`.
5. `orchestrator` runs cross-artifact analysis and, if approved, syncs issues.
6. `fullstack-builder` executes in an isolated worktree, test-first, with subagents for independent tasks.
7. `qa-test-engineer` collects fresh verification evidence against the definition of done.
8. `code-reviewer` decides the merge, and `--strict` traceability must pass.
9. `orchestrator` converges spec and code and runs the retrospective.

## Gates

- Do not plan before the design is approved and high-impact gaps are closed.
- Do not execute before analysis has no CRITICAL finding and the traceability script has no HIGH finding.
- Do not claim done without fresh evidence for each criterion.
- Do not write to the issue tracker or deploy without explicit human approval.

## Runtime Hints

- Codex and Claude Code: one worktree per user story, subagents only for tasks marked parallel.
- Hermes: schedule the retrospective stage as a follow-up run.
- GitHub Actions: run `python scripts/sdlc_trace.py --target . --strict` as a required check.
