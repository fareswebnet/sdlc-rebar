# sdlc-implementation-planning (compact)

When: Plan implementation for scoped code changes by identifying affected files, architecture boundaries, data migrations, tests, risks, rollback, validation commands, and sequencing.

Goal: Make code work predictable before editing files.

Steps:
1. Read relevant specs, code, tests, architecture notes, and local conventions.
2. Map impacted modules, contracts, data, permissions, and user-visible behavior.
3. Choose the smallest implementation sequence that preserves working states.
4. Define tests, manual checks, migration safety, and rollback path.
5. Call out assumptions and blockers before execution.

Never:
- Do not implement from memory when the repo can provide the answer.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.
