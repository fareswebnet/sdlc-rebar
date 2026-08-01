---
name: sdlc-data-database-architecture
description: Design data architecture, database schemas, ownership, source of truth, migrations, indexes, audit trails, retention, multi-tenant data isolation, analytics events, and data quality controls. Use before implementing persistence, reporting, imports, billing, compliance workflows, or data-heavy features.
---

# SDLC Data Database Architecture

## Purpose

Make data ownership, persistence, and evolution explicit.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Map domain entities, bounded contexts, ownership, and source-of-truth decisions.
2. Design logical and physical schema with constraints, indexes, migrations, and audit requirements.
3. Define transaction boundaries, consistency expectations, retention, deletion, and privacy rules.
4. Plan multi-tenant isolation, backups, restore, imports, exports, and reporting needs.
5. Connect operational data to product analytics and compliance evidence.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/architecture/data-model.md, docs/architecture/database-design.md, docs/security/data-protection.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not add shared tables or cross-context writes without an explicit ownership and consistency decision.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
