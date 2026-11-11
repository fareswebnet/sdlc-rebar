---
name: sdlc-systematic-debugging
description: Debug by finding root cause before fixing: reproduce, trace data flow, test one hypothesis at a time. Use for any bug, test failure, or build break, especially under time pressure or after a failed fix.
---

# SDLC Systematic Debugging

## Purpose

Replace guess-and-patch with an evidence-driven investigation that fixes the cause once.

## Workflow

1. Investigate: read the full error and stack trace, reproduce with exact steps, inspect recent changes, and note the environment.
2. In multi-component systems, add temporary diagnostic output at each boundary to find which layer breaks, then trace backward from the bad value to its source.
3. Compare: find similar working code, list differences, and check assumptions and dependencies.
4. Hypothesize: state one specific hypothesis (`X is the cause because Y`), make the smallest change that tests it, and change one variable at a time.
5. If the hypothesis is wrong, revert and form a new one; do not stack fixes.
6. Fix: write a failing reproduction test via `sdlc-test-driven-development`, apply a single targeted fix at the root cause, and verify with `sdlc-verification-before-completion`.
7. After three failed fix attempts, stop and question the architecture or the premise with the user before a fourth attempt.

## Outputs

- Primary artifacts: Root-cause statement with evidence, regression test, minimal fix, removal of diagnostics, notes for the incident or decision log.

## Guardrails

- No fixes before Phase 1 evidence exists.
- Do not bundle refactors with the fix.
- Treat `quick fix now, investigate later` as a trigger to slow down, not speed up.
- Remove temporary logging and probes before finishing.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| Quick fix first, investigate later | The first fix sets the pattern; do it right once. |
| I see the problem | Seeing a symptom is not knowing the cause; verify with evidence. |
| One more attempt | After three failures, question the architecture. |

## Handoff

`sdlc-test-driven-development` for the regression test; `sdlc-incident-support-feedback` for production causes.

## Provenance

Adapted idea, extended beyond the source, not copied text: superpowers systematic-debugging (four phases, three-strikes rule). Provenance is tracked in `docs/references/method-sources.md`.
