# sdlc-code-change-execution (compact)

When: Implement scoped code changes preserving local patterns, tests, boundaries, and user changes, with verification evidence.

Goal: Make disciplined changes that satisfy the spec and survive review.

Steps:
1. Confirm the implementation plan or create one if missing.
2. Edit the smallest coherent set of files using existing patterns and helper APIs.
3. Add or update tests proportional to risk and blast radius.
4. Run targeted validation, then broader validation when shared behavior changed.
5. Summarize changed behavior, tests run, risks, and any unverified assumptions.

Never:
- Do not revert unrelated user changes or perform broad refactors outside the request.
