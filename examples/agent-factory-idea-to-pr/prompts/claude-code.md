# Claude Code Prompt

```text
Use the AI SDLC suite as the delivery method.

Role:
- start as agents/orchestrator.yaml
- hand off conceptually to product-strategist, domain-architect, ux-ui-designer, solution-architect, fullstack-builder, qa-test-engineer, security-reviewer, and code-reviewer as needed

Harness:
- harnesses/app-idea-to-production.yaml

App idea:
ReleasePilot is a B2B SaaS app for small product-engineering teams. It reads a feature brief, acceptance criteria, CI status, risk notes, and deployment context, then produces a release-readiness view with missing gates, rollback notes, and post-release checks.

Deliver:
- docs/product/prd.md
- docs/product/bdd/release-readiness.feature
- docs/architecture/application-architecture.md
- docs/architecture/data-model.md
- docs/engineering/implementation-plan.md
- first vertical slice implementation
- tests and validation notes
- PR body and review gate

Stop before production deployment.
Ask before adding dependencies, changing secrets, running migrations, touching customer data, or invoking deployment commands.
```
