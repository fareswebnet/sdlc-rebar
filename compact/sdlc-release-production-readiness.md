# sdlc-release-production-readiness (compact)

When: Prepare release and production readiness reviews including rollout strategy, migration safety, feature flags, rollback, changelog, monitoring, runbooks, support readiness, security gates, and go/no-go decisions.

Goal: Make releases deliberate, observable, and reversible where possible.

Steps:
1. Summarize what is changing, who is impacted, and what success looks like.
2. Check tests, security, migrations, performance, observability, support, docs, and rollback readiness.
3. Choose rollout strategy: full, phased, canary, blue/green, feature flag, or manual migration.
4. Define go/no-go criteria and owner for each risk.
5. Prepare release notes and post-release monitoring plan.

Never:
- Do not release when rollback, monitoring, or customer impact is unknown for a material change.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.
