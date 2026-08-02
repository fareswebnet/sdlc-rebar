---
name: releasepilot-implementation
description: Implement the approved ReleasePilot Signal Clustering first slice by turning accepted red tests green inside scoped paths, preserving architecture boundaries, feature flag control, tenant isolation, and validation evidence.
---

# ReleasePilot Implementation

## Purpose

Implement only the approved vertical slice.

## Allowed Scope

- `src/domain/signal-clustering`
- `src/app/signal-clustering`
- `tests/domain`
- `tests/components`
- `docs`

## Workflow

1. Read BDD, red tests, architecture, and feature flag.
2. Implement the smallest code path that turns the red tests green.
3. Keep clustering logic isolated in domain services.
4. Keep spec generation behind accepted human validation.
5. Run lint, typecheck, tests, and targeted UI tests when available.
6. Record validation and residual risk.

## Guardrails

- Do not add dependencies without approval.
- Do not create migrations without approval.
- Do not edit auth, billing, secrets, deployment, or customer communication.
- Do not broaden scope to external connectors.
