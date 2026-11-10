---
name: sdlc-design-brainstorming
description: Turn a rough idea or feature request into an approved design through collaborative dialogue: explore context, ask one question at a time, compare two or three approaches with trade-offs, present the design in reviewable sections, and obtain explicit approval before any planning or code. Use before any creative or behavior-changing work, including changes that seem too small to need design.
---

# SDLC Design Brainstorming

## Purpose

Prevent building the wrong thing by making design approval a hard gate, scaled to the size of the change.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Explore the project first: existing docs, recent commits, constraints, similar features, and conventions.
2. If the request spans several independent subsystems, say so and decompose into separate specs before refining details.
3. Ask clarifying questions one at a time, preferring multiple choice, focused on purpose, constraints, and success criteria.
4. Propose two or three approaches with trade-offs and a recommendation, and apply YAGNI: remove features that are not needed to meet the goal.
5. Present the design in sections sized to their complexity (architecture, components, data flow, error handling, testing) and confirm after each section.
6. Write the approved design to `docs/product/` or the feature spec folder, self-review it for ambiguity, contradictions, and scope creep, then ask the user to review the written file.
7. Only after approval, hand off to `$sdlc-implementation-planning` or `$sdlc-task-breakdown`; never jump straight to code.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Approved design document with decisions and rejected alternatives, then a handoff to planning.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Hard gate: no implementation, scaffolding, or code until the user approves the design.
- A small change gets a short design, not a skipped one.
- In existing code, follow current structure; propose targeted improvements only where they affect the work.
- Keep each design unit understandable and testable in isolation, with clear interfaces.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| This is too simple for a design | Simple work hides unexamined assumptions; keep the design short. |
| The user clearly wants X | Confirm with one question before building. |

## Handoff

`$sdlc-spec-clarification` for gaps, then `$sdlc-implementation-planning`.

## Source Guidance

Adapted idea, extended beyond the source, not copied text: superpowers brainstorming (hard gate, one question at a time, approaches before design). Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
