---
name: releasepilot-domain
description: Model the ReleasePilot Signal Clustering domain with ubiquitous language, bounded contexts, invariants, data ownership, tenant boundaries, and human-validation rules before behavior examples are accepted.
---

# ReleasePilot Domain

## Purpose

Make product semantics and ownership explicit before implementation.

## Workflow

1. Define domain concepts: signal, source, cluster, evidence, confidence, conflict, validation decision, and spec draft.
2. Map bounded contexts and ownership.
3. Record invariants and illegal transitions.
4. Identify tenant and privacy boundaries.
5. Hand off to BDD with a stable vocabulary.

## Outputs

- `docs/architecture/domain-model.md`
- `docs/architecture/context-map.md`

## Guardrails

- Do not let the clustering context own final roadmap priority.
- Do not let generated specs bypass human validation.
- Treat feedback text as sensitive data.
