---
name: sdlc-architecture-rfc
description: Create architecture RFCs, C4-style diagrams, ADR candidates, viewpoints, constraints, risks, trade-off tables, and architecture review packets. Use when choosing or changing architecture style, platform boundaries, module structure, integrations, data ownership, or production-critical technical decisions.
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
