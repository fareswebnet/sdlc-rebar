# MCP Integration

Use MCP and connectors to give agents authorized, current, private context without scraping or relying on memory.

## Recommended Connectors

| Domain | Useful tools | Default permission |
|---|---|---|
| Source control | GitHub PRs, issues, checks, releases | read-write for issues and PR comments, protected write for branches |
| Backlog | Linear, Jira, GitHub Issues | read-write after triage approval |
| Documentation | Confluence, Notion, Google Drive | read-first |
| Design | Figma | read-only until design automation is mature |
| Communication | Slack, Teams, email | read-only for signal capture; human approval for outbound messages |
| Observability | Sentry, Datadog, Grafana, OpenTelemetry backends | read-only for triage |
| Data | PostgreSQL, warehouse, BI tools | read-only, scoped, audited |
| Cloud | AWS, GCP, Azure, deployment platforms | read-only by default; production write requires approval |
| Feature flags | LaunchDarkly or equivalent | read-write only for approved rollout tasks |

## Connector Policy

- Prefer read-only for research, triage, review, and post-release learning.
- Use write permissions only for narrow workflows with explicit ownership.
- Keep credentials in the runtime's secure connector configuration, not in repo files.
- Record which connector evidence informed a decision when the decision affects release, security, privacy, or compliance.

## Context Packs

For autonomous runs, prepare a compact context pack:

- product docs and PRD
- BDD examples
- architecture and ADRs
- current diff or branch
- CI output
- relevant issues or tickets
- observability evidence when production is involved
- known constraints and approval requirements

The orchestrator should pass only the relevant subset to each specialist agent.
