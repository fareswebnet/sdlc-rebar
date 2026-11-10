# OpenClaw Integration

Use OpenClaw as an adapter when its workspace, skills registry, or MCP-mediated Claude Code control is part of the team workflow.

## Fit

OpenClaw is useful for experimentation and cross-tool coordination. Treat this repository as the method source of truth, and OpenClaw as one possible runtime shell.

## Install Skills

Mirror the suite into the OpenClaw workspace skills directory:

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -R skills/sdlc-* ~/.openclaw/workspace/skills/
```

Add the agent and harness folders as workspace context files or keep them in the target repository.

## Workspace Context

Add or update workspace `AGENTS.md` with:

```md
Use `ai-sdlc-skills` for full software delivery.

Route work through:
- `harnesses/app-idea-to-production.yaml`
- `harnesses/feature-to-production.yaml`
- `harnesses/spec-driven-delivery.yaml` for traceable, test-first, evidence-gated delivery
- `harnesses/legacy-migration.yaml` and `harnesses/system-merge.yaml` for registry-driven migrations and merges
- `harnesses/production-feedback-loop.yaml`

Use `agents/*.yaml` for role, permission, gate, and handoff guidance.
GitHub issues, branches, PRs, and checks remain the source of truth.
```

## Claude Code Adapter

If using an OpenClaw skill that controls Claude Code through MCP, keep the task bounded:

```text
Use agents/fullstack-builder.yaml and the implementation plan.
Ask Claude Code to edit only files needed for the first vertical slice.
Run validation and return the diff summary, tests, and residual risks.
```

## Safety Defaults

- start with docs, tests, and review workflows before broad write permissions
- keep production commands outside autonomous OpenClaw sessions
- require explicit approval for secrets, dependency additions, migrations, deploys, payments, and customer data changes
