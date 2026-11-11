# sdlc-legacy-reverse-engineering (compact)

When: Recover the behavior of a legacy system from code, data, logs, and observed execution into a business-rule matrix with stable ids, data flows, and unknowns, before any target design.

Goal: Turn implicit behavior into explicit, id-addressable rules that tests can prove and owners can approve.

Steps:
1. Work from the registry: process one batch of lines at a time and trace each from entry point through validation, business logic…
2. Extract rules as `RG-<SOURCE>-<NNN>` entries: condition, effect, inputs, source file and line, owner question, and risk class (R1…
3. Capture data lifecycle: tables touched, state transitions, events emitted, jobs and schedules, external calls, and files produced.
4. Mine tests, fixtures, production data shapes, logs, and support tickets for behavior the code hides; label each rule as observed…
5. Record bugs and accidental behavior separately as `LEGACY_DEFECT` with a decision: reproduce only if the business depends on it…
6. List unknowns and contradictions as questions with an owner; they block the batch only if they affect an R1 rule.
7. Link each rule to registry keys and, later, to scenarios and tests so `sdlc-traceability-ledger` can check coverage.

Never:
- Do not read the legacy's intent into code; mark inferred rules as inferred until confirmed.
- Every R1 rule needs a second reader or an executed oracle before it is approved.
- Do not copy legacy defects by default; record the decision to improve or reproduce.
- Keep secrets and customer data out of extracted fixtures.

Next: `sdlc-characterization-testing` to prove the rules, `sdlc-bdd-specifications` to express them as scenarios.
