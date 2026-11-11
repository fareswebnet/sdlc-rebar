---
name: sdlc-project-constitution
description: Create or amend a versioned project constitution of non-negotiable engineering, quality, security, and AI-usage principles that every later spec, plan, task, and review is checked against. Use at project kickoff, when principles drift, or before onboarding agents to a repository.
---

# SDLC Project Constitution

## Purpose

Give humans and agents one short, testable set of rules that outrank convenience, so plans and reviews have something concrete to be checked against.

## Workflow

1. Collect candidate principles from the user, existing docs, `AGENTS.md`, ADRs, CI config, and incident history.
2. Keep only principles that are specific, testable, and costly to violate (for example: tests precede implementation, no secrets in repo, every public API has a contract, tenants never share data paths).
3. Phrase each as `MUST` / `SHOULD` with a one-line rationale and the check that proves compliance (CI job, review checklist item, test).
4. Version the document with semantic versioning: MAJOR for removed or redefined principles, MINOR for added principles, PATCH for wording fixes. Record the amendment date and reason.
5. Run a consistency sweep: list templates, harnesses, agents, and skills that cite the constitution and flag any that now contradict it. Report them; do not silently edit them.
6. Park non-governance requests (features, refactors, deployments) as deferred intents with the suggested next skill instead of executing them.

## Outputs

- Primary artifacts: `docs/governance/constitution.md`, amendment entry in `docs/governance/decision-log.md`, sync-impact list.

## Guardrails

- Do not invent principles the team has not accepted; propose and ask.
- A principle without a verification method is a wish; either add the check or drop it.
- Amendments to MUST rules require human approval and a recorded rationale.
- Keep the constitution under about two pages; long rule lists are ignored.

## Handoff

`sdlc-design-brainstorming` to start features under the principles; `sdlc-cross-artifact-analysis` to enforce them.

## Provenance

Adapted idea, extended beyond the source, not copied text: speckit-constitution (versioned principles, sync-impact sweep, scope guard). Provenance is tracked in `docs/references/method-sources.md`.
