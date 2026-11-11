# sdlc-identity-access-multitenancy (compact)

When: Design authentication, authorization, RBAC, ABAC, permissions, account lifecycle, tenant isolation, privileged access, impersonation, admin access, and negative access tests.

Goal: Treat identity and authorization as domain and security models, not route-level afterthoughts.

Steps:
1. Define identities, accounts, organizations, tenants, roles, permissions, and lifecycle states.
2. Model authorization as business rules with explicit denies and escalation paths.
3. Review tenant isolation across database, files, cache, logs, queues, analytics, and backups.
4. Define privileged access, impersonation, break-glass, audit, and approval rules.
5. Create negative access tests and cross-tenant regression checks.

Never:
- Do not rely on UI hiding as an authorization control.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.
