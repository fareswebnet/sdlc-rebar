---
name: sdlc-identity-access-multitenancy
description: Design authentication, authorization, RBAC, ABAC, permissions, account lifecycle, tenant isolation, privileged access, impersonation, admin access, and negative access tests. Use for SaaS, B2B, fintech, internal tools, admin back-office, or any product with users, roles, organizations, or tenants.
---

# SDLC Identity Access Multitenancy

## Purpose

Treat identity and authorization as domain and security models, not route-level afterthoughts.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Define identities, accounts, organizations, tenants, roles, permissions, and lifecycle states.
2. Model authorization as business rules with explicit denies and escalation paths.
3. Review tenant isolation across database, files, cache, logs, queues, analytics, and backups.
4. Define privileged access, impersonation, break-glass, audit, and approval rules.
5. Create negative access tests and cross-tenant regression checks.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/security/identity-access.md, docs/security/tenant-isolation.md, docs/quality/access-control-tests.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not rely on UI hiding as an authorization control.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
