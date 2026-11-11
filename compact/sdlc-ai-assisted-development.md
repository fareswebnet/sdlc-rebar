# sdlc-ai-assisted-development (compact)

When: Plan and govern AI-assisted software development with context engineering, task decomposition, agent roles, coding guardrails, review loops, traceability from spec to code, and output evaluation.

Goal: Use AI coding agents as supervised engineering workflows, not free-form generators.

Steps:
1. Prepare the minimum useful context: repo conventions, specs, architecture, tests, constraints, and risks.
2. Decompose work into bounded tasks with expected artifacts and validation commands.
3. Assign agent roles only when independent perspectives add value.
4. Require spec-to-code traceability, tests, review, and rollback awareness.
5. Use `agents/` role definitions for permissions, autonomy level, outputs, gates, and handoffs.
6. Use `harnesses/` to coordinate multi-stage autonomous flows and `integrations/` to adapt the same flow to Codex, Claude Code…
7. Evaluate outputs for correctness, maintainability, security, UX, and scope control.

Never:
- Do not allow AI-generated changes that invent APIs, ignore local patterns, skip tests, or refactor outside…
- Do not equate high automation with unlimited authority: production, secrets, destructive migrations…
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.
