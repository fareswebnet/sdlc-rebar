# sdlc-systematic-debugging (compact)

When: Debug by finding root cause before fixing: reproduce, trace data flow, test one hypothesis at a time.

Goal: Replace guess-and-patch with an evidence-driven investigation that fixes the cause once.

Steps:
1. Investigate: read the full error and stack trace, reproduce with exact steps, inspect recent changes, and note the environment.
2. In multi-component systems, add temporary diagnostic output at each boundary to find which layer breaks, then trace backward from…
3. Compare: find similar working code, list differences, and check assumptions and dependencies.
4. Hypothesize: state one specific hypothesis (`X is the cause because Y`), make the smallest change that tests it, and change one…
5. If the hypothesis is wrong, revert and form a new one; do not stack fixes.
6. Fix: write a failing reproduction test via `sdlc-test-driven-development`, apply a single targeted fix at the root cause, and…
7. After three failed fix attempts, stop and question the architecture or the premise with the user before a fourth attempt.

Never:
- No fixes before Phase 1 evidence exists.
- Do not bundle refactors with the fix.
- Treat `quick fix now, investigate later` as a trigger to slow down, not speed up.
- Remove temporary logging and probes before finishing.

Next: `sdlc-test-driven-development` for the regression test; `sdlc-incident-support-feedback` for production causes.
