---
name: sdlc-release-production-readiness
description: Prepare release and production readiness reviews including rollout strategy, migration safety, feature flags, rollback, changelog, monitoring, runbooks, support readiness, security gates, and go/no-go decisions. Use before production release or significant customer-facing deployment.
---

# SDLC Release Production Readiness

## Purpose

Make releases deliberate, observable, and reversible where possible.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Summarize what is changing, who is impacted, and what success looks like.
2. Check tests, security, migrations, performance, observability, support, docs, and rollback readiness.
3. Choose rollout strategy: full, phased, canary, blue/green, feature flag, or manual migration.
4. Define go/no-go criteria and owner for each risk.
5. Prepare release notes and post-release monitoring plan.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/delivery/release-plan.md, docs/delivery/production-readiness.md, docs/operations/runbooks/`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not release when rollback, monitoring, or customer impact is unknown for a material change.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
