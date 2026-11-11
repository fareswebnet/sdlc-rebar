---
name: sdlc-architecture-rfc
description: Write architecture RFCs with C4 diagrams, ADR candidates, trade-offs, and risks for review. Use when choosing or changing architecture style, platform boundaries, integrations, or data ownership.
---

# SDLC Architecture RFC

## Purpose

Make significant architecture choices explicit, reviewable, and traceable.

## Workflow

1. Identify stakeholders, concerns, quality attributes, constraints, and context.
2. Describe current state and proposed architecture at the right abstraction level.
3. Compare alternatives, consequences, reversibility, and migration path.
4. Use C4-style context/container/component views when diagrams help communication.
5. Promote accepted decisions into ADRs and implementation constraints.

## Outputs

- Primary artifacts: `docs/architecture/rfc/, docs/architecture/adr/, docs/architecture/c4/`.

## Guardrails

- Do not present architecture as a preference; document the forces, trade-offs, and consequences.
