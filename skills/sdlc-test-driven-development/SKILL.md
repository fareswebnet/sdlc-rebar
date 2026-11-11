---
name: sdlc-test-driven-development
description: Enforce red-green-refactor: write one failing test, watch it fail, write minimal code to pass, then refactor. Use when implementing any behavior change or bug fix, before writing production code.
---

# SDLC Test-Driven Development

## Purpose

Make tests drive design and prove behavior, so passing tests mean something.

## Workflow

1. RED: write one minimal test for one behavior, with a clear name and real code rather than mocks where possible.
2. Verify RED: run it and confirm it fails because the feature is missing, not because of a typo or setup error. A test that passes immediately proves nothing; fix the test.
3. GREEN: write the simplest code that passes. No extra features, no speculative options.
4. Verify GREEN: run the full relevant suite; the new test and all existing tests must pass with clean output.
5. REFACTOR: remove duplication and improve names while keeping tests green; do not add behavior.
6. Repeat for the next behavior. Map each test back to a BDD scenario or requirement id when one exists.
7. For bugs: write a failing test that reproduces the bug first, then fix it; the test is the regression guard.

## Outputs

- Primary artifacts: Failing-then-passing tests tied to requirements, minimal implementation, refactor notes, evidence of the red and green runs.

## Guardrails

- No production code without a failing test first. If code was written first, discard it and restart from the test rather than adapting it.
- Do not keep untested code as a reference; the rule applies to the letter.
- Avoid testing mock behavior; mock only what is external, slow, or nondeterministic.
- Exceptions (throwaway prototypes, generated code, configuration) require explicit human agreement.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| Too simple to test | Simple code breaks; the test takes under a minute. |
| I'll add tests after | Tests written after pass immediately and prove nothing. |
| I already wrote the code | Discard it and restart from the failing test. |

## Handoff

`sdlc-verification-before-completion` after each green cycle; `sdlc-code-review` for the diff.

## Provenance

Adapted idea, extended beyond the source, not copied text: superpowers test-driven-development (iron law, verify-red/verify-green). Provenance is tracked in `docs/references/method-sources.md`.
