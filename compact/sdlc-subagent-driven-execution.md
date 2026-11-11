# sdlc-subagent-driven-execution (compact)

When: Execute a task list by dispatching a fresh subagent per task with exactly the context it needs, followed by a spec-compliance review and a code-quality review, and by running genuinely independent work in parallel.

Goal: Keep each agent focused and each change reviewed, so large plans execute reliably without context pollution.

Steps:
1. Read the task list once; extract each task's full text, context, files, and validation commands, and create tracking items.
2. Group tasks by independence: tasks with disjoint files and no data dependency may run in parallel; others run sequentially.
3. Dispatch one implementer per task with a self-contained brief: goal, exact files, constraints, tests, and the expected report…
4. Handle implementer status: DONE, DONE_WITH_CONCERNS (read the concerns), NEEDS_CONTEXT (supply it and retry), BLOCKED (change…
5. After each task run two reviews in order: spec compliance (nothing missing, nothing extra), then code quality.
6. Choose the lightest sufficient model for each role; reserve stronger models for integration, design, and review of risky tasks.
7. Verify the integrated result with `sdlc-verification-before-completion`, then finish the branch via…

Never:
- Never run two implementers that edit the same files at once.
- Do not skip either review stage or accept `close enough` on spec compliance.
- Subagents must not inherit unrelated context; construct their input deliberately.
- Human gates from the harness still apply: dependencies, migrations, secrets, and deployments need approval.

Next: `sdlc-agent-context-engineering` for briefs; `sdlc-branch-worktree-lifecycle` and `sdlc-spec-convergence` after the run.
