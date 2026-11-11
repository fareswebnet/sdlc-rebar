# sdlc-project-constitution (compact)

When: Create or amend a versioned constitution of non-negotiable engineering, quality, security, and AI principles.

Goal: Give humans and agents one short, testable set of rules that outrank convenience, so plans and reviews have something concrete to be checked against.

Steps:
1. Collect candidate principles from the user, existing docs, `AGENTS.md`, ADRs, CI config, and incident history.
2. Keep only principles that are specific, testable, and costly to violate (for example: tests precede implementation, no secrets in…
3. Phrase each as `MUST` / `SHOULD` with a one-line rationale and the check that proves compliance (CI job, review checklist item…
4. Version the document with semantic versioning: MAJOR for removed or redefined principles, MINOR for added principles, PATCH for…
5. Run a consistency sweep: list templates, harnesses, agents, and skills that cite the constitution and flag any that now…
6. Park non-governance requests (features, refactors, deployments) as deferred intents with the suggested next skill instead of…

Never:
- Do not invent principles the team has not accepted; propose and ask.
- A principle without a verification method is a wish; either add the check or drop it.
- Amendments to MUST rules require human approval and a recorded rationale.
- Keep the constitution under about two pages; long rule lists are ignored.

Next: `sdlc-design-brainstorming` to start features under the principles; `sdlc-cross-artifact-analysis` to enforce them.
