---
name: sdlc-api-versioning-deprecation
description: Manage API and event contract evolution: classify changes as compatible or breaking, choose a versioning approach, run contract tests with consumer-driven expectations, and execute deprecation with telemetry, notice periods, and sunset dates. Use when changing a public or cross-team API, replacing a legacy interface during migration, or supporting several client versions.
---

# SDLC API Versioning And Deprecation

## Purpose

Let contracts change on purpose, with consumers informed and protected.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Inventory consumers and their versions from gateway logs, client registries, or contract tests; unknown consumers are a risk to record.
2. Classify each change: additive and optional is compatible; removing, renaming, changing type, semantics, required fields, or error behavior is breaking. Use a diff tool on the OpenAPI or AsyncAPI document in CI.
3. Prefer compatible evolution (tolerant readers, additive fields, defaults); pick a versioning approach (URL, header, or event schema version) only when breaking is unavoidable.
4. Add consumer-driven contract tests and run them against the provider before merge.
5. For deprecation: announce with date, publish a migration guide, add deprecation and sunset headers or schema flags, and measure remaining traffic per consumer.
6. Support old and new in parallel for a stated period; remove only when telemetry shows zero or accepted residual use, with a rollback window.
7. During legacy migration, keep the legacy contract until the target serves it identically in `sdlc-characterization-testing`, then deprecate on schedule.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Versioning policy, breaking-change CI check, consumer registry, deprecation notices and sunset calendar.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Never change semantics under the same version silently.
- Do not remove an endpoint with live consumers without agreed notice.
- Error formats and status codes are part of the contract.
- Customer-facing deprecation notices need human approval.

## Handoff

`sdlc-api-integration-contracts` for contract design, `sdlc-cutover-rollback` when replacing a legacy interface.

## Source Guidance

Original to this suite; informed by semantic versioning and consumer-driven contract practice. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
