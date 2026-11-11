---
name: sdlc-domain-modeling
description: Discover and model the business domain using DDD vocabulary, ubiquitous language, entities, value objects, aggregates, invariants, state transitions, policies, and domain services. Use before architecture, database design, BDD, API contracts, or implementation in domains with meaningful business rules.
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
