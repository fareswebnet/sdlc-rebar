# sdlc-spec-clarification (compact)

When: Find and resolve underspecified areas in a PRD, feature spec, or BDD set by asking a small number of high-impact questions, one at a time, with a recommended answer, and writing each decision back into the spec.

Goal: Remove costly ambiguity early, with a bounded interview that ends in recorded decisions instead of an open-ended discussion.

Steps:
1. Scan the spec against a coverage taxonomy: scope and non-goals, actors and permissions, data and lifecycle, edge and failure…
2. Mark each area Clear, Partial, or Missing; rank gaps by impact on architecture, tests, security, or cost, times uncertainty.
3. Ask at most five questions per session, one at a time.
4. After each answer, update the spec immediately in a `Clarifications` section dated with the session, and fix the affected…
5. Stop when critical gaps are closed, the user says stop, or the question budget is spent.
6. If the codebase can answer a question, read the code instead of asking the user.

Never:
- Never ask more than one question at a time or pile on low-impact style questions.
- Do not start planning while a high-impact gap is Missing unless the user explicitly accepts the risk.
- Record answers verbatim enough to audit; do not paraphrase decisions into something new.
- Respect depth: Lean runs a single round, Enterprise-ready logs owner and date for every decision.

Next: `sdlc-requirements-checklist` to test the clarified spec, then `sdlc-implementation-planning`.
