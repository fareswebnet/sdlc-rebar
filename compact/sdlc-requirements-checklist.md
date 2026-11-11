# sdlc-requirements-checklist (compact)

When: Generate a checklist that tests the quality of written requirements (completeness, clarity, measurability, edge cases), not the implementation.

Goal: Treat requirements as the system under test: every checklist item asks whether the requirement is well written, never whether the code works.

Steps:
1. Pick the domain and audience (security, UX, API, data, AI, performance, compliance) and the depth: author self-check, peer…
2. Read the spec, plan, and BDD files; extract each requirement and the scenario that exercises it.
3. Write checklist items as questions about the text, each tagged with a quality dimension: Completeness, Clarity, Consistency…
4. Reference the exact requirement id or section in every item; mark gaps explicitly when no id exists.
5. Run the checklist against the spec, tick what passes, and convert each failure into a clarification question or backlog fix.
6. Store one checklist per domain so they can be re-run after each spec change.

Never:
- Bad item: `Verify the login button works`.
- Do not generate implementation test cases here; hand those to `sdlc-test-strategy`.
- Cap each checklist to the items that change a decision; avoid exhaustive boilerplate lists.
- Cite the requirement, not general best practice, so reviewers can act on each item.

Next: `sdlc-spec-clarification` for failures, `sdlc-implementation-planning` once items pass.
