# sdlc-task-breakdown (compact)

When: Turn an approved spec and plan into a dependency-ordered task list per user story: exact file paths, parallel markers, test-first order.

Goal: Make the plan executable: each task is small, unambiguous, traceable to a requirement, and runnable by an agent or human without guessing.

Steps:
1. Load the plan, spec, data model, contracts, and BDD scenarios; confirm user stories carry priorities (P1, P2, P3).
2. Create phases: Setup, Foundations (blocking prerequisites), then one phase per user story in priority order, then Polish and…
3. Within a story, order tests first, then models, services, interfaces, and integration.
4. Write each task as `- [ ] T### [P?] [US#] Action with exact/file/path`.
5. Add a checkpoint after each story: the slice must be demonstrable and testable on its own, and a story must never require a later…
6. State the dependency graph and the MVP cut (usually story P1 only), plus validation commands per checkpoint.
7. Cross-check: every requirement, scenario, and contract maps to at least one task, and every task maps back to one of them.

Never:
- No vague tasks such as `implement backend`; name the file and the observable result.
- Do not mark tasks parallel when they edit the same file or depend on unfinished outputs.
- Do not generate tests the spec did not ask for in Lean mode; in Standard and above, tests follow risk.
- Keep tasks small enough to review in one diff (target one commit).

Next: `sdlc-cross-artifact-analysis` and `sdlc-traceability-ledger` before execution; `sdlc-tasks-to-issues` when tracked externally.
