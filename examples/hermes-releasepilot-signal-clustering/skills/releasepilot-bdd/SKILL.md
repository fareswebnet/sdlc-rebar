---
name: releasepilot-bdd
description: Convert the ReleasePilot Signal Clustering domain model into concrete behavior examples and Gherkin scenarios covering clustering, conflicts, confidence, human validation, spec generation, and tenant isolation.
---

# ReleasePilot BDD

## Purpose

Turn the desired behavior into examples that can drive implementation and tests.

## Workflow

1. Start from domain concepts and product intent.
2. Write examples before implementation.
3. Cover happy paths, low confidence, conflicts, rejection, split or merge, and tenant isolation.
4. Map each scenario to requirements and expected tests.
5. Stop for human acceptance before red tests or code.

## Outputs

- `features/signal-clustering.feature`
- `docs/product/requirements-traceability.md`

## Guardrails

- Do not write generic examples that cannot fail.
- Do not omit tenant isolation.
- Do not allow spec generation before human validation.
