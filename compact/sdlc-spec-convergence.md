# sdlc-spec-convergence (compact)

When: Compare the current codebase to the spec, plan, and task list to find what was actually built, what is partial, and what remains, then append the missing work as new tasks.

Goal: Close the loop between intent and code so remaining work is explicit instead of assumed.

Steps:
1. Read the spec, plan, tasks, and BDD scenarios; list each requirement with its expected observable behavior.
2. Inspect the repository and tests for evidence per requirement: implemented and tested, implemented only, partial, missing, or…
3. Run the existing test suite and acceptance scenarios; treat failing or absent tests as evidence, not assumptions.
4. Classify drift: code ahead of spec (propose spec update), code behind spec (new task), or deliberate deviation (record a…
5. Append new tasks to the task list using the same id and format rules as `sdlc-task-breakdown`; never renumber or delete completed…
6. Summarize the delta: done, remaining, drifted, risky, and the next safe step.

Never:
- Evidence must be a file, test, or command output; do not mark done on the basis of a plausible-looking diff.
- Do not rewrite the spec to match the code without a recorded decision.
- Do not implement the new tasks in the same step; hand them to execution.
- Stay within the feature scope; list unrelated findings separately.

Next: `sdlc-subagent-driven-execution` to build appended tasks; `sdlc-delivery-retrospective` for recurring drift.
