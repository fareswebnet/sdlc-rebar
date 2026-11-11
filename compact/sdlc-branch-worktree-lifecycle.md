# sdlc-branch-worktree-lifecycle (compact)

When: Start work in an isolated git worktree with a verified baseline; finish by merge, PR, keep, or discard.

Goal: Keep the main checkout safe and give every change a clean start and a deliberate ending.

Steps:
1. Detect whether you are already in a linked worktree or the main checkout; reuse an existing isolated workspace when present.
2. Prefer the project's declared worktree location; if none, use an ignored directory (verify with `git check-ignore`) so worktree…
3. Create the branch and worktree, run project setup, and run the test suite to record a clean baseline.
4. Work in small commits tied to task ids.
5. To finish: verify tests with `sdlc-verification-before-completion`, then offer exactly these options: merge locally, push and…
6. Discard requires typed confirmation listing the branch and commits being lost.
7. Never force-push or rewrite shared history without explicit approval.

Never:
- Do not start on a dirty baseline without telling the user.
- Never delete work without explicit confirmation of what is lost.
- Do not merge with failing tests.
- Keep unrelated user changes untouched.

Next: `sdlc-code-review` before merge; `sdlc-definition-of-done` for release.
