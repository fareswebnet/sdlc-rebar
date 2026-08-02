---
name: releasepilot-architecture
description: Define the ReleasePilot Signal Clustering architecture, ADR, data ownership, API boundaries, UX states, feature flag, observability hooks, and rollout constraints before implementation begins.
---

# ReleasePilot Architecture

## Purpose

Create enough architecture to implement safely without over-designing the first slice.

## Workflow

1. Choose the smallest architecture that satisfies the BDD contract.
2. Define data ownership and tenant boundaries.
3. Keep LLM or embedding usage behind interfaces.
4. Define route, component, and service boundaries.
5. Define feature flag, rollback, and observability.

## Outputs

- `docs/architecture/adr/0001-signal-clustering.md`
- `docs/architecture/application-architecture.md`
- `docs/architecture/data-model.md`
- `docs/delivery/feature-flags.md`
- `docs/operations/observability.md`

## Guardrails

- Do not add external connectors in the first slice.
- Do not introduce background jobs without proof of need.
- Do not change auth or tenant boundaries without approval.
