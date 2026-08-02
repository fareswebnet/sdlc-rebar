# Claude Code Integration

Use Claude Code as a terminal coding agent for repo-local execution, implementation, tests, and MCP-connected workflows.

## Install Skills

Claude Code does not need the skills to live in a Codex-specific path. Keep this repository checked out and reference the relevant skill folders in prompts, or mirror the `skills/` tree into the target repo under `.agents/skills/` for cross-tool consistency.

## Project Memory

Run Claude Code setup for the target repository and keep the generated project memory concise. Add this guidance to `CLAUDE.md`:

```md
Use the AI SDLC suite as the delivery method.

Before implementation, produce or update:
- product behavior or BDD examples
- affected architecture, data, API, and security boundaries
- validation commands
- rollback notes

Use the agent role files under `agents/` to decide whether the task is product, domain, architecture, build, QA, security, release, or production feedback work.
```

## Suggested Prompts

```text
Use the role `agents/fullstack-builder.yaml` and the skills `sdlc-implementation-planning` and `sdlc-code-change-execution`.
Implement only the first vertical slice described in docs/engineering/implementation-plan.md.
Run the validation commands and report residual risk.
```

```text
Use the role `agents/code-reviewer.yaml`.
Review the current diff against docs/product/prd.md, docs/product/bdd, and docs/architecture.
Lead with blocking findings and missing tests.
```

## MCP Connectors

Use MCP for authorized private context:

- GitHub issues, PRs, and checks
- Linear or Jira backlog
- Slack support signal when approved
- observability tools
- read-only databases or warehouses
- docs and design tools

Prefer read-only connectors until the workflow and permission model are stable.

## Safety Defaults

- use planning or read-only mode for architecture, security, and production tasks
- use broader autonomy only in isolated branches or worktrees
- require approval for dependency installation, secrets, migrations, production deploys, payments, and customer data changes
