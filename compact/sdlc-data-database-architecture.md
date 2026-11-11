# sdlc-data-database-architecture (compact)

When: Design data architecture, database schemas, ownership, source of truth, migrations, indexes, audit trails, retention, multi-tenant data isolation, analytics events, and data quality controls.

Goal: Make data ownership, persistence, and evolution explicit.

Steps:
1. Map domain entities, bounded contexts, ownership, and source-of-truth decisions.
2. Design logical and physical schema with constraints, indexes, migrations, and audit requirements.
3. Define transaction boundaries, consistency expectations, retention, deletion, and privacy rules.
4. Plan multi-tenant isolation, backups, restore, imports, exports, and reporting needs.
5. Connect operational data to product analytics and compliance evidence.

Never:
- Do not add shared tables or cross-context writes without an explicit ownership and consistency decision.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.
