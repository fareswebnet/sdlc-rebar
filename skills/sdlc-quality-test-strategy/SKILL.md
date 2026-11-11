---
name: sdlc-quality-test-strategy
description: Define quality strategy, acceptance tests, unit tests, integration tests, contract tests, e2e tests, regression risk, exploratory testing, non-functional testing, and quality gates. Use when planning validation for a feature, release, refactor, incident fix, architecture change, or BDD specification.
---

# SDLC Quality Test Strategy

## Purpose

Test what matters by risk, behavior, and quality attributes rather than coverage theater.

## Workflow

1. Map requirements, BDD scenarios, architecture boundaries, and risk areas.
2. Choose the right test level for each behavior: unit, integration, contract, e2e, exploratory, or manual.
3. Define non-functional checks for security, performance, accessibility, reliability, and compatibility where relevant.
4. Prioritize regression coverage around critical user and business workflows.
5. Set a quality gate for merge and release.

## Outputs

- Primary artifacts: `docs/quality/test-strategy.md, docs/quality/acceptance-tests.md, docs/quality/regression-risk.md`.

## Guardrails

- Do not equate high coverage percentage with sufficient product quality.
