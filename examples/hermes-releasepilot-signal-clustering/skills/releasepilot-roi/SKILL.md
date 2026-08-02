---
name: releasepilot-roi
description: Measure the ReleasePilot Signal Clustering agentic delivery workflow after merge or preview by comparing cycle time, agent cost, review rework, defect escape, accepted clusters, spec edit rate, and skill improvement opportunities.
---

# ReleasePilot ROI

## Purpose

Turn production and delivery signals into learning.

## Metrics

- cycle time from idea to PR
- agent run cost
- human review time
- PR rework rate
- defect escape rate
- accepted cluster rate
- rejected cluster rate
- spec draft edit rate
- incidents linked to clustering output

## Workflow

1. Collect approved delivery and product signals.
2. Compare actual results to expected outcomes.
3. Identify repeated failure modes.
4. Propose skill or gate improvements with evidence.
5. Record decisions in the governance log.

## Guardrails

- Do not infer customer impact without evidence.
- Do not modify durable skills without human review.
- Do not access private customer data unless approval is explicit.
