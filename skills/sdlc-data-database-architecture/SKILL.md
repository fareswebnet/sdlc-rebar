---
name: sdlc-data-database-architecture
description: Design data architecture, database schemas, ownership, source of truth, migrations, indexes, audit trails, retention, multi-tenant data isolation, analytics events, and data quality controls. Use before implementing persistence, reporting, imports, billing, compliance workflows, or data-heavy features.
---

# SDLC Data Database Architecture

## Purpose

Make data ownership, persistence, and evolution explicit.

## Workflow

1. Map domain entities, bounded contexts, ownership, and source-of-truth decisions.
2. Design logical and physical schema with constraints, indexes, migrations, and audit requirements.
3. Define transaction boundaries, consistency expectations, retention, deletion, and privacy rules.
4. Plan multi-tenant isolation, backups, restore, imports, exports, and reporting needs.
5. Connect operational data to product analytics and compliance evidence.

## Outputs

- Primary artifacts: `docs/architecture/data-model.md, docs/architecture/database-design.md, docs/security/data-protection.md`.

## Guardrails

- Do not add shared tables or cross-context writes without an explicit ownership and consistency decision.
