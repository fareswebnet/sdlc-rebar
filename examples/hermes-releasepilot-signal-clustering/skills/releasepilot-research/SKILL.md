---
name: releasepilot-research
description: Research and frame the ReleasePilot Signal Clustering feature by clarifying product intent, target users, evidence sources, assumptions, non-goals, and success metrics before any architecture or implementation work starts.
---

# ReleasePilot Research

## Purpose

Clarify the product problem before agents create specs or code.

## Inputs

- raw feature request
- user segment
- known feedback sources
- existing product strategy docs
- approved research sources

## Workflow

1. Define the user, job-to-be-done, and pain.
2. Separate evidence from assumptions.
3. Record non-goals for the first slice.
4. Identify the riskiest product and data assumptions.
5. Define measurable outcomes for the preview.

## Outputs

- `docs/product/problem-statement.md`
- `docs/product/assumptions.md`
- `docs/product/strategy.md`

## Guardrails

- Do not invent market evidence.
- Do not access real customer data without approval.
- Do not move to implementation until product intent and non-goals are explicit.
