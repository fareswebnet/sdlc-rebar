# Codex Prompt

```text
Use $sdlc-delivery-system and $sdlc-ai-assisted-development.

Run harnesses/app-idea-to-production.yaml for this app idea:

ReleasePilot is a B2B SaaS app for small product-engineering teams. It reads a feature brief, acceptance criteria, CI status, risk notes, and deployment context, then produces a release-readiness view with missing gates, rollback notes, and post-release checks.

Goal:
- create the product docs, BDD examples, architecture, data model, and implementation plan
- implement only the first vertical slice in an isolated branch or worktree
- prepare a PR summary and review gate
- stop before production deployment

Use the agent role files in agents/.
Use examples/agent-factory-idea-to-pr/artifacts/task-graph.yaml as the target shape.
Require human approval for dependency additions, migrations, secrets, customer data, payments, and production deployment.
```
