# sdlc-test-driven-development (compact)

When: Enforce the red-green-refactor cycle for features, bug fixes, and behavior changes: write one failing test, watch it fail for the right reason, write the minimal code to pass, then refactor with tests green.

Goal: Make tests drive design and prove behavior, so passing tests mean something.

Steps:
1. RED: write one minimal test for one behavior, with a clear name and real code rather than mocks where possible.
2. Verify RED: run it and confirm it fails because the feature is missing, not because of a typo or setup error.
3. GREEN: write the simplest code that passes.
4. Verify GREEN: run the full relevant suite; the new test and all existing tests must pass with clean output.
5. REFACTOR: remove duplication and improve names while keeping tests green; do not add behavior.
6. Repeat for the next behavior.
7. For bugs: write a failing test that reproduces the bug first, then fix it; the test is the regression guard.

Never:
- No production code without a failing test first.
- Do not keep untested code as a reference; the rule applies to the letter.
- Avoid testing mock behavior; mock only what is external, slow, or nondeterministic.
- Exceptions (throwaway prototypes, generated code, configuration) require explicit human agreement.

Next: `sdlc-verification-before-completion` after each green cycle; `sdlc-code-review-quality-gate` for the diff.
