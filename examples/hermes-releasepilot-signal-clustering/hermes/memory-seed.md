# ReleasePilot Memory Seed

Use this as a concise seed for a dedicated Hermes profile.

## Stable Product Facts

- Product: ReleasePilot.
- Audience: founder-CTOs, product leads, and engineering leads in small teams that ship often.
- Promise: turn product and production signals into decision-ready delivery artifacts.
- Current feature: Signal Clustering.
- Non-goal for first slice: fully automated prioritization without human validation.

## Stable Engineering Rules

- Use BDD examples before implementation.
- Use TDD red tests before production code.
- Keep implementation inside the Signal Clustering bounded context unless a human approves a wider change.
- Treat feedback text as potentially sensitive customer data.
- Keep tenant isolation mandatory.
- Use feature flags for rollout.
- Do not deploy from an autonomous run.

## Quality Definition

A feature is ready for review only when behavior, data ownership, tests, security risk, rollout path, observability, and residual risk are explicit.
