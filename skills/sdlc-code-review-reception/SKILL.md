---
name: sdlc-code-review-reception
description: Handle code review feedback with technical rigor: read all feedback, restate it, verify each item against the codebase, ask about anything unclear, push back with evidence when feedback is wrong, and implement one item at a time with tests. Use when receiving review comments from humans or agents, before applying suggested changes.
---

# SDLC Code Review Reception

## Purpose

Turn review feedback into correct changes without performative agreement or blind implementation.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Read all feedback completely before acting; do not implement the first item and keep reading.
2. Restate each requirement in your own words; ask for clarification on any item you cannot restate, before touching code.
3. Verify each suggestion against the actual code, tests, and requirements; check whether it breaks behavior or violates the spec or YAGNI.
4. Respond with technical facts: agree and fix, ask a precise question, or push back with evidence. Avoid filler praise or thanks.
5. Implement in priority order: blockers, simple fixes, then complex changes, one item at a time, re-running tests after each.
6. Reply on the review thread with what changed and the commit, so the reviewer can re-check.
7. If feedback conflicts with an earlier human decision, stop and raise the conflict instead of choosing silently.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Item-by-item response log, commits per fix, test evidence, list of pushbacks with rationale.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Unverified suggestions are hypotheses, not orders.
- External reviewer suggestions get the same scrutiny as agent suggestions.
- Do not mark a thread resolved without a fix or an agreed decision.
- Never implement partially understood feedback.

## Handoff

`sdlc-verification-before-completion` after fixes; `sdlc-delivery-retrospective` for repeated findings.

## Source Guidance

Adapted idea, extended beyond the source, not copied text: superpowers receiving-code-review and requesting-code-review. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
