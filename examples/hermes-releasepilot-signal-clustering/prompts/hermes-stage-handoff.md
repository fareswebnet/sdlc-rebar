# Hermes Stage Handoff Prompts

Use these prompts when a full run needs to be resumed or when a stage should be delegated to a subagent.

## Domain And BDD

```text
Use agents/domain-architect.yaml with skills sdlc-domain-modeling, sdlc-bounded-context-map, and sdlc-bdd-specifications.

Feature: ReleasePilot Signal Clustering.

Produce:
- domain model
- bounded context map
- BDD scenarios
- requirements traceability

Do not implement. Stop when BDD examples are ready for human acceptance.
```

## Red Test Writer

```text
Use agents/qa-test-engineer.yaml with skills sdlc-quality-test-strategy and sdlc-bdd-specifications.

Inputs:
- accepted BDD scenarios
- architecture decision
- feature flag definition

Write tests that fail for the right reason before production code exists.

Allowed writes:
- tests/domain
- tests/components
- docs/quality

Do not modify implementation files.
```

## Scoped Implementation

```text
Use agents/fullstack-builder.yaml with skills sdlc-code-change-execution and sdlc-quality-test-strategy.

Implement only the Signal Clustering first slice.

Allowed paths:
- src/domain/signal-clustering
- src/app/signal-clustering
- tests/domain
- tests/components
- docs

Do not add dependencies, migrations, auth changes, billing changes, secrets, deployment config, or external connectors.

Goal:
Turn the accepted red tests green, then refactor without widening scope.
```

## Independent Review

```text
Use agents/code-reviewer.yaml and agents/security-reviewer.yaml.

Review:
- diff scope
- BDD traceability
- test evidence
- tenant isolation
- sensitive feedback handling
- feature flag and rollback
- residual risk

Return:
- blocking findings
- non-blocking follow-ups
- merge recommendation
- production gate status
```
