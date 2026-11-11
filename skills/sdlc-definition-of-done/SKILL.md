---
name: sdlc-definition-of-done
description: Define a Definition of Done scaled by depth and risk, each criterion naming its proving evidence. Use when setting team agreements, closing a story or release, or when done is argued not shown.
---

# SDLC Definition Of Done

## Purpose

Replace subjective 'done' with a short checklist whose every line has a proof.

## Workflow

1. Read `docs/references/depth-matrix.md` and pick the depth for this change from risk, blast radius, regulation, and reversibility.
2. Build the criteria set in three levels: task (tests green, diff reviewed, docs touched), story (acceptance scenarios pass, accessibility and security checks, telemetry added), release (rollback tested, runbook, SLO impact, owner sign-off).
3. Attach an evidence type to each criterion: command output, CI link, screenshot, trace id, review thread, or decision-log entry.
4. Add risk-triggered criteria: migrations need a rollback rehearsal, new dependencies need a license record, AI features need an eval result, privileged paths need a security review.
5. At closure, walk the list; any unmet criterion is either completed, explicitly waived by a named owner with a reason, or turns the item back to in progress.
6. Record waivers in `docs/governance/decision-log.md` and review waiver patterns each retrospective.

## Outputs

- Primary artifacts: `docs/governance/definition-of-done.md` per depth, evidence checklist attached to each PR or release.

## Guardrails

- A criterion without evidence is removed or fixed, not kept as decoration.
- Waivers need an owner and a reason; silent skipping is a process failure.
- Keep Lean to under ten lines; Enterprise-ready may be longer but still evidence-first.
- Do not weaken criteria mid-sprint to make a deadline.

## Handoff

`sdlc-verification-before-completion` to produce the evidence, `sdlc-definition-of-done` for release-level criteria.

## Provenance

Original to this suite; informed by the evidence-first discipline of Superpowers verification and the Spec Kit constitution gates, scaled by risk. Provenance is tracked in `docs/references/method-sources.md`.
