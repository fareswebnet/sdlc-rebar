---
name: sdlc-bdd-specifications
description: Run behavior discovery, example mapping, and Gherkin Given/When/Then scenarios as living documentation. Use for unclear requirements, testable acceptance criteria, or PRD-to-test traceability.
---

# SDLC BDD Specifications

## Purpose

Use concrete examples to close ambiguity between business, product, design, engineering, and QA.

## Workflow

1. Identify actors, goals, rules, examples, counterexamples, and open questions.
2. Use example mapping to separate rules, scenarios, edge cases, and unknowns.
3. Write scenarios in business language, not UI implementation language unless UI behavior is the point.
4. Connect every scenario to acceptance tests and requirements.
5. Keep scenarios small, deterministic, and valuable as living documentation.

## Outputs

- Primary artifacts: `docs/product/bdd/, docs/quality/acceptance-tests.md, docs/product/requirements-traceability.md`.

## Guardrails

- Do not generate code from a story whose critical examples and edge cases are still unknown.
