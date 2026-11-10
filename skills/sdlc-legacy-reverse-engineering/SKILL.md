---
name: sdlc-legacy-reverse-engineering
description: Recover the behavior of a legacy system from code, data, logs, and observed execution into a business-rule matrix with stable ids, data flows, and unknowns, before any target design. Use when documentation is missing or stale, when estimating a migration, or when two systems must be compared rule by rule.
---

# SDLC Legacy Reverse Engineering

## Purpose

Turn implicit behavior into explicit, id-addressable rules that tests can prove and owners can approve.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Work from the registry: process one batch of lines at a time and trace each from entry point through validation, business logic, persistence, side effects, and output.
2. Extract rules as `RG-<SOURCE>-<NNN>` entries: condition, effect, inputs, source file and line, owner question, and risk class (R1 money, security, or compliance; R2 workflows and CRUD; R3 presentation).
3. Capture data lifecycle: tables touched, state transitions, events emitted, jobs and schedules, external calls, and files produced.
4. Mine tests, fixtures, production data shapes, logs, and support tickets for behavior the code hides; label each rule as observed, inferred, or confirmed by the business.
5. Record bugs and accidental behavior separately as `LEGACY_DEFECT` with a decision: reproduce only if the business depends on it, otherwise improve in the target.
6. List unknowns and contradictions as questions with an owner; they block the batch only if they affect an R1 rule.
7. Link each rule to registry keys and, later, to scenarios and tests so `sdlc-traceability-ledger` can check coverage.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/migration/rules/<source>-rules.md`, data-flow notes, defect list, open-question list with owners.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not read the legacy's intent into code; mark inferred rules as inferred until confirmed.
- Every R1 rule needs a second reader or an executed oracle before it is approved.
- Do not copy legacy defects by default; record the decision to improve or reproduce.
- Keep secrets and customer data out of extracted fixtures.

## Handoff

`sdlc-characterization-testing` to prove the rules, `sdlc-bdd-specifications` to express them as scenarios.

## Source Guidance

Original to this suite; informed by spec-mining and retro-documentation practice. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
