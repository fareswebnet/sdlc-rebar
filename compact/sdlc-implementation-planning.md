# sdlc-implementation-planning (compact)

When: Plan scoped code changes: affected files, boundaries, migrations, tests, risks, rollback, validation commands, sequencing.

Goal: Make code work predictable before editing files.

Steps:
1. Read relevant specs, code, tests, architecture notes, and local conventions.
2. Map impacted modules, contracts, data, permissions, and user-visible behavior.
3. Choose the smallest implementation sequence that preserves working states.
4. Define tests, manual checks, migration safety, and rollback path.
5. Call out assumptions and blockers before execution.

Never:
- Do not implement from memory when the repo can provide the answer.
