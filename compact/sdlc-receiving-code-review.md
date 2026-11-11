# sdlc-receiving-code-review (compact)

When: Handle received review feedback rigorously: verify each item against the code, push back with evidence, implement one at a time.

Goal: Turn review feedback into correct changes without performative agreement or blind implementation.

Steps:
1. Read all feedback completely before acting; do not implement the first item and keep reading.
2. Restate each requirement in your own words; ask for clarification on any item you cannot restate, before touching code.
3. Verify each suggestion against the actual code, tests, and requirements; check whether it breaks behavior or violates the spec or…
4. Respond with technical facts: agree and fix, ask a precise question, or push back with evidence.
5. Implement in priority order: blockers, simple fixes, then complex changes, one item at a time, re-running tests after each.
6. Reply on the review thread with what changed and the commit, so the reviewer can re-check.
7. If feedback conflicts with an earlier human decision, stop and raise the conflict instead of choosing silently.

Never:
- Unverified suggestions are hypotheses, not orders.
- External reviewer suggestions get the same scrutiny as agent suggestions.
- Do not mark a thread resolved without a fix or an agreed decision.
- Never implement partially understood feedback.

Next: `sdlc-verification-before-completion` after fixes; `sdlc-delivery-retrospective` for repeated findings.
