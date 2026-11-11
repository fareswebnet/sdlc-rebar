---
name: sdlc-code-review-quality-gate
description: Perform code review and quality gates focused on correctness, maintainability, architecture boundaries, tests, security, performance, UX impact, migrations, observability, and release risk. Use before merge, before release, after AI-generated code, or when auditing a change set.
---

# SDLC Code Review Quality Gate

## Purpose

Find defects and risk before they reach users.

## Workflow

1. Review the diff against requirements, BDD scenarios, architecture decisions, and local code patterns.
2. Prioritize bugs, regressions, missing tests, security issues, and release blockers.
3. Check maintainability, coupling, naming, error handling, logging, and migration safety.
4. Separate blocking findings from improvements and stylistic preferences.
5. Require validation evidence or clearly state residual risk.

## Outputs

- Primary artifacts: `review findings, merge gate decision, residual risk notes`.

## Guardrails

- Do not approve code whose behavior cannot be connected to a spec or tested expectation.
