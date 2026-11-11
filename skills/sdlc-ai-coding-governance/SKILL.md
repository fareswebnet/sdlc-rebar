---
name: sdlc-ai-coding-governance
description: Govern AI-assisted coding: task decomposition, agent roles, guardrails, review loops. Use when coding with agents, splitting work across agents, or preventing code drift from specs.
---

# SDLC AI Coding Governance

## Purpose

Use AI coding agents as supervised engineering workflows, not free-form generators.

## Workflow

1. Prepare the minimum useful context: repo conventions, specs, architecture, tests, constraints, and risks.
2. Decompose work into bounded tasks with expected artifacts and validation commands.
3. Assign agent roles only when independent perspectives add value.
4. Require spec-to-code traceability, tests, review, and rollback awareness.
5. Use `agents/` role definitions for permissions, autonomy level, outputs, gates, and handoffs.
6. Use `harnesses/` to coordinate multi-stage autonomous flows and `integrations/` to adapt the same flow to Codex, Claude Code, Hermes, OpenClaw, GitHub Actions, MCP, or a custom runtime.
7. Evaluate outputs for correctness, maintainability, security, UX, and scope control.

## Outputs

- Primary artifacts: `docs/engineering/ai-development-plan.md, docs/product/requirements-traceability.md, docs/quality/validation-plan.md`.
- Agent task graph with selected roles, autonomy level, runtime adapter, permissions, gates, and stop conditions when automation is requested.

## Guardrails

- Do not allow AI-generated changes that invent APIs, ignore local patterns, skip tests, or refactor outside scope.
- Do not equate high automation with unlimited authority: production, secrets, destructive migrations, payments, dependency additions, and customer data require human approval.
