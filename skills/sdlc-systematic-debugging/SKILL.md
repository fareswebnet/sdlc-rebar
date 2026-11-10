---
name: sdlc-systematic-debugging
description: Debug bugs, test failures, build breaks, and unexpected behavior by finding the root cause before proposing fixes: read errors fully, reproduce reliably, check recent changes, trace data flow, form one hypothesis at a time, and verify. Use for any technical issue, especially under time pressure, after a failed fix, or when the cause is not understood.
---

# SDLC Systematic Debugging

## Purpose

Replace guess-and-patch with an evidence-driven investigation that fixes the cause once.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Investigate: read the full error and stack trace, reproduce with exact steps, inspect recent changes, and note the environment.
2. In multi-component systems, add temporary diagnostic output at each boundary to find which layer breaks, then trace backward from the bad value to its source.
3. Compare: find similar working code, list differences, and check assumptions and dependencies.
4. Hypothesize: state one specific hypothesis (`X is the cause because Y`), make the smallest change that tests it, and change one variable at a time.
5. If the hypothesis is wrong, revert and form a new one; do not stack fixes.
6. Fix: write a failing reproduction test via `$sdlc-test-driven-development`, apply a single targeted fix at the root cause, and verify with `$sdlc-verification-before-completion`.
7. After three failed fix attempts, stop and question the architecture or the premise with the user before a fourth attempt.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Root-cause statement with evidence, regression test, minimal fix, removal of diagnostics, notes for the incident or decision log.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

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

`$sdlc-test-driven-development` for the regression test; `$sdlc-incident-support-feedback` for production causes.

## Source Guidance

Adapted idea, extended beyond the source, not copied text: superpowers systematic-debugging (four phases, three-strikes rule). Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
