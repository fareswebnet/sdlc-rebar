---
name: sdlc-delivery-retrospective
description: Run an evidence-based retrospective after a feature, release, or incident that compares plan with outcome, mines review findings, waivers, rework, and escapes, and converts the lessons into concrete changes to the constitution, definition of done, skills, templates, or CI checks. Use at the end of a release or sprint, after incidents, or when the same defect type keeps recurring.
---

# SDLC Delivery Retrospective

## Purpose

Close the loop so each delivery makes the next one cheaper and safer, with changes landing in the system rather than in meeting notes.

## Workflow

1. Collect evidence, not memories: trace report, review comments, CI failures, waivers, rework commits, escaped defects, incident timelines, and delivery metrics (lead time, change failure rate, time to restore).
2. Compare plan with outcome: scope delivered, tasks added by convergence, estimates versus actuals, and requirements that changed after build.
3. Cluster the problems by cause: unclear spec, missing test, weak review, environment, tooling, or skill gap. Look for patterns across the last several deliveries.
4. For each cluster choose the cheapest durable fix: new checklist item, tighter template, constitution amendment, CI gate, skill revision, or context pack update.
5. When a fix would be a new prohibition stacked on earlier ones, rewrite the underlying instruction instead of adding another rule.
6. Assign each action an owner, due date, and a measurable check; add it to the backlog or decision log.
7. Re-check actions at the next retrospective and drop those that did not change the numbers.

## Outputs

- Primary artifacts: `docs/governance/retrospective-<date>.md`, updated templates or skills, decision-log entries, action list with owners.

## Guardrails

- Blameless: analyze process and system causes, not individuals.
- No action item without an owner and a way to know it worked.
- Prefer changes enforced by tooling over reminders.
- Keep it short; a retrospective that produces no change is wasted effort.

## Handoff

`sdlc-project-constitution` for principle changes, `sdlc-skill-evaluation` for skill updates, `sdlc-incident-support-feedback` for production lessons.

## Provenance

Original to this suite; informed by DORA-style metrics and the self-improving loop implied by Spec Kit constitution amendments and Superpowers skill iteration. Provenance is tracked in `docs/references/method-sources.md`.
