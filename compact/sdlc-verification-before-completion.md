# sdlc-verification-before-completion (compact)

When: Require fresh evidence before claiming work is done: run the proving command in full, read output and exit code, then report.

Goal: Make every status claim traceable to evidence produced now, not remembered or assumed.

Steps:
1. Identify which command or check proves the claim (tests, build, lint, type check, migration dry run, acceptance scenario).
2. Run the complete command freshly; partial runs and earlier results do not count.
3. Read the full output, check the exit code, and count failures and warnings.
4. Compare against the requirement list line by line for `done` claims, not just the test result.
5. State the actual status with the evidence.
6. For delegated work, verify the diff and re-run checks yourself instead of trusting a subagent report.
7. For bug fixes, confirm the original reproduction now passes and that a regression test fails without the fix.

Never:
- No `should work`, `probably`, or `looks right` in a completion claim.
- Passing lint is not passing build; passing unit tests is not passing acceptance.
- Do not commit, open a PR, or move to the next task before the check ran.
- Honest failure reports are acceptable; unverified success claims are not.

Next: `sdlc-definition-of-done` for the full criteria; `sdlc-branch-worktree-lifecycle` to finish.
