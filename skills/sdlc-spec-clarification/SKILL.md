---
name: sdlc-spec-clarification
description: Find and resolve underspecified areas in a PRD, feature spec, or BDD set by asking a small number of high-impact questions, one at a time, with a recommended answer, and writing each decision back into the spec. Use before architecture or planning when requirements feel vague, or when a plan keeps stalling on open questions.
---

# SDLC Spec Clarification

## Purpose

Remove costly ambiguity early, with a bounded interview that ends in recorded decisions instead of an open-ended discussion.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Scan the spec against a coverage taxonomy: scope and non-goals, actors and permissions, data and lifecycle, edge and failure cases, non-functional targets, integrations, UX states, compliance, terminology, and measurable success.
2. Mark each area Clear, Partial, or Missing; rank gaps by impact on architecture, tests, security, or cost, times uncertainty.
3. Ask at most five questions per session, one at a time. Offer a recommended answer with reasoning and two or three alternatives; accept a short reply or `yes` for the recommendation.
4. After each answer, update the spec immediately in a `Clarifications` section dated with the session, and fix the affected requirement, scenario, or glossary entry in place.
5. Stop when critical gaps are closed, the user says stop, or the question budget is spent. Report a coverage table: resolved, deferred, still outstanding.
6. If the codebase can answer a question, read the code instead of asking the user.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Updated spec or PRD with a `Clarifications` log, coverage summary, list of deferred questions with their risk.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Never ask more than one question at a time or pile on low-impact style questions.
- Do not start planning while a high-impact gap is Missing unless the user explicitly accepts the risk.
- Record answers verbatim enough to audit; do not paraphrase decisions into something new.
- Respect depth: Lean runs a single round, Enterprise-ready logs owner and date for every decision.

## Handoff

`$sdlc-requirements-checklist` to test the clarified spec, then `$sdlc-implementation-planning`.

## Source Guidance

Adapted idea, extended beyond the source, not copied text: speckit-clarify (bounded, sequential, recommendation-first interview). Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
