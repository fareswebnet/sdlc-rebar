---
name: sdlc-requirements-checklist
description: Generate a domain-specific checklist that tests the quality of written requirements - completeness, clarity, consistency, measurability, and coverage of edge cases - rather than testing the implementation. Use before sign-off of a PRD or spec, before planning, or when a reviewer asks whether requirements are good enough to build from.
---

# SDLC Requirements Checklist

## Purpose

Treat requirements as the system under test: every checklist item asks whether the requirement is well written, never whether the code works.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Pick the domain and audience (security, UX, API, data, AI, performance, compliance) and the depth: author self-check, peer review, or release gate.
2. Read the spec, plan, and BDD files; extract each requirement and the scenario that exercises it.
3. Write checklist items as questions about the text, each tagged with a quality dimension: Completeness, Clarity, Consistency, Measurability, Coverage, Dependencies, Assumptions.
4. Reference the exact requirement id or section in every item; mark gaps explicitly when no id exists.
5. Run the checklist against the spec, tick what passes, and convert each failure into a clarification question or backlog fix.
6. Store one checklist per domain so they can be re-run after each spec change.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/quality/requirements-checklist.md` per domain, with traceability references and a failure summary.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Bad item: `Verify the login button works`. Good item: `Is the failure behavior for expired sessions specified with a measurable timeout?`
- Do not generate implementation test cases here; hand those to `sdlc-quality-test-strategy`.
- Cap each checklist to the items that change a decision; avoid exhaustive boilerplate lists.
- Cite the requirement, not general best practice, so reviewers can act on each item.

## Handoff

`sdlc-spec-clarification` for failures, `sdlc-implementation-planning` once items pass.

## Source Guidance

Adapted idea, extended beyond the source, not copied text: speckit-checklist ('unit tests for English'). Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
