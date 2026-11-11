# sdlc-code-change-execution (compact)

When: Execute scoped code changes in a repository while preserving local patterns, tests, architecture boundaries, user changes, migration safety, and verification evidence.

Goal: Make disciplined changes that satisfy the spec and survive review.

Steps:
1. Confirm the implementation plan or create one if missing.
2. Edit the smallest coherent set of files using existing patterns and helper APIs.
3. Add or update tests proportional to risk and blast radius.
4. Run targeted validation, then broader validation when shared behavior changed.
5. Summarize changed behavior, tests run, risks, and any unverified assumptions.

Never:
- Do not revert unrelated user changes or perform broad refactors outside the request.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.
