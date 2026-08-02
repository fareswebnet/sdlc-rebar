# Pipeline: Production Feedback Loop

Use this pipeline for incidents, support tickets, analytics anomalies, reliability issues, cost spikes, performance bottlenecks, and post-release learning.

## Outcome

Turn production signals into:

- incident or feedback summary
- root-cause analysis
- roadmap or backlog change
- fix PR when warranted
- updated runbook, test, alert, or dashboard
- explicit learning captured in docs

## Sequence

1. Run `devops-sre` to capture severity, blast radius, affected journeys, and telemetry evidence.
2. Run `product-strategist` when the signal changes priority, UX, pricing, onboarding, or roadmap assumptions.
3. Run `solution-architect` when remediation touches architecture, data, context boundaries, or technical debt.
4. Run `fullstack-builder` for the scoped fix.
5. Run `qa-test-engineer` to add recurrence tests or targeted regression checks.
6. Run `release-manager` for controlled rollout and post-release checks.
7. Feed the learning back into docs, runbooks, and future PRD assumptions.

## Gates

- Emergency fixes still need scope, rollback, and validation evidence.
- Customer-facing communication requires human approval.
- Recurring incidents should create architecture or debt items, not only hotfixes.
- Product analytics changes must preserve event quality and metric definitions.

## Runtime Hints

- Codex: use scheduled tasks or non-interactive runs for triage summaries and regression sweeps.
- Claude Code: use MCP connectors for issue tracker and observability context when available.
- Hermes: use scheduled automations for daily or weekly production learning reports.
- OpenClaw: keep workspace context files aligned with the repo's current incident and runbook docs.
