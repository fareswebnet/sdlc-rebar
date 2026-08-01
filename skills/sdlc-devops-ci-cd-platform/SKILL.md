---
name: sdlc-devops-ci-cd-platform
description: Design developer environment, CI/CD, build, test, lint, typecheck, security scan, artifact provenance, environments, secrets, infrastructure as code, preview deployments, and developer experience. Use when setting up or improving delivery platform, pipelines, environments, or deployment automation.
---

# SDLC DevOps CI CD Platform

## Purpose

Make build, test, preview, and deploy boring enough for fast teams.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Inventory local setup, dependencies, scripts, env vars, services, and onboarding friction.
2. Design pipeline stages for build, lint, typecheck, tests, security, artifacts, and deploy.
3. Define environment strategy: local, preview, staging, production, data, secrets, and isolation.
4. Add supply-chain controls appropriate to risk: lockfiles, provenance, SBOM, pinned actions, permissions.
5. Measure developer experience and DORA-relevant flow.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/delivery/ci-cd-platform.md, docs/delivery/environment-strategy.md, docs/engineering/developer-onboarding.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not add deployment automation without a rollback and secrets strategy.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
