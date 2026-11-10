---
name: sdlc-definition-of-done
description: Define and apply a Definition of Done that scales with Lean, Standard, or Enterprise-ready depth and risk, where every criterion names the evidence that proves it. Use when setting team working agreements, before closing a task, story, or release, or when 'done' is argued instead of demonstrated.
---

# SDLC Definition Of Done

## Purpose

Replace subjective 'done' with a short checklist whose every line has a proof.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Read `docs/references/depth-matrix.md` and pick the depth for this change from risk, blast radius, regulation, and reversibility.
2. Build the criteria set in three levels: task (tests green, diff reviewed, docs touched), story (acceptance scenarios pass, accessibility and security checks, telemetry added), release (rollback tested, runbook, SLO impact, owner sign-off).
3. Attach an evidence type to each criterion: command output, CI link, screenshot, trace id, review thread, or decision-log entry.
4. Add risk-triggered criteria: migrations need a rollback rehearsal, new dependencies need a license record, AI features need an eval result, privileged paths need a security review.
5. At closure, walk the list; any unmet criterion is either completed, explicitly waived by a named owner with a reason, or turns the item back to in progress.
6. Record waivers in `docs/governance/decision-log.md` and review waiver patterns each retrospective.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/governance/definition-of-done.md` per depth, evidence checklist attached to each PR or release.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- A criterion without evidence is removed or fixed, not kept as decoration.
- Waivers need an owner and a reason; silent skipping is a process failure.
- Keep Lean to under ten lines; Enterprise-ready may be longer but still evidence-first.
- Do not weaken criteria mid-sprint to make a deadline.

## Handoff

`$sdlc-verification-before-completion` to produce the evidence, `$sdlc-release-production-readiness` for release-level criteria.

## Source Guidance

Original to this suite; informed by the evidence-first discipline of Superpowers verification and the Spec Kit constitution gates, scaled by risk. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
