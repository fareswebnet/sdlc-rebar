# sdlc-code-review (compact)

When: Review a change set as a quality gate: correctness, architecture, tests, security, performance, release risk.

Goal: Find defects and risk before they reach users.

Steps:
1. Review the diff against requirements, BDD scenarios, architecture decisions, and local code patterns.
2. Prioritize bugs, regressions, missing tests, security issues, and release blockers.
3. Check maintainability, coupling, naming, error handling, logging, and migration safety.
4. Separate blocking findings from improvements and stylistic preferences.
5. Require validation evidence or clearly state residual risk.

Never:
- Do not approve code whose behavior cannot be connected to a spec or tested expectation.
