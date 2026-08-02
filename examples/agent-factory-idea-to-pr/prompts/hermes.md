# Hermes Prompt

```bash
hermes chat --worktree --skills sdlc-delivery-system,sdlc-ai-assisted-development \
  -q "Run harnesses/app-idea-to-production.yaml for ReleasePilot.

ReleasePilot is a B2B SaaS app for small product-engineering teams. It reads a feature brief, acceptance criteria, CI status, risk notes, and deployment context, then produces a release-readiness view with missing gates, rollback notes, and post-release checks.

Use agents/orchestrator.yaml as the entrypoint.
Use examples/agent-factory-idea-to-pr/artifacts/task-graph.yaml as the target shape.
Create product docs, BDD examples, architecture notes, implementation plan, first vertical slice, tests, PR body, and review gate.
Stop before production deployment.
Require human approval for dependencies, migrations, secrets, customer data, payments, and deployment."
```
