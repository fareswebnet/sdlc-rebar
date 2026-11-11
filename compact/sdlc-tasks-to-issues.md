# sdlc-tasks-to-issues (compact)

When: Convert an approved task list into dependency-linked issues in GitHub, GitLab, Jira, or Linear, and keep status synchronized with the repo task file, after explicit human approval.

Goal: Keep the repo task list and the tracker consistent without creating noise or duplicate work.

Steps:
1. Confirm `docs/engineering/tasks.md` passed `sdlc-cross-artifact-analysis` and `python scripts/sdlc_trace.py`; do not sync a plan…
2. Verify the remote: show the target repository or project and wait for approval before creating anything.
3. Create one epic per feature and one issue per user story; keep individual tasks as checklist items unless they need separate…
4. Put in each issue: goal, acceptance scenarios, requirement ids, task ids, dependencies, validation command, and the MVP flag.
5. Link blockers and parallel groups; label by priority and story id.
6. Record issue numbers back into the task file so the mapping is two-way, and detect duplicates before creating new ones.
7. On later runs, reconcile status: closed issues with open tasks, and done tasks with open issues, are reported rather than…

Never:
- Creating issues is an external write: require explicit approval for the exact remote and scope.
- Never create issues in a repository that does not match the local remote without confirmation.
- Do not paste secrets or customer data into issue bodies.
- No bulk edits of existing issues without a diff and approval.

Next: `sdlc-subagent-driven-execution` to run the tasks, `sdlc-delivery-roadmap-backlog` for prioritization.
