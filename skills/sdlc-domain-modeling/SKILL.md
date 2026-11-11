---
name: sdlc-domain-modeling
description: Model the business domain with DDD: ubiquitous language, entities, aggregates, invariants, state transitions. Use before architecture, database, or BDD work in domains with real business rules.
---

# SDLC Domain Modeling

## Purpose

Make the business model explicit before the software model hardens.

## Workflow

1. Extract domain terms, actors, actions, lifecycle states, and policies.
2. Identify entities, value objects, aggregates, commands, events, and invariants.
3. Separate domain rules from UI, persistence, integration, and reporting concerns.
4. Find ambiguous terms and align them with a ubiquitous language.
5. Feed bounded contexts, BDD scenarios, database design, and API contracts.

## Outputs

- Primary artifacts: `docs/architecture/domain-model.md, docs/architecture/ubiquitous-language.md`.

## Guardrails

- Do not design tables, APIs, or services before the core domain terms and invariants are clear.
