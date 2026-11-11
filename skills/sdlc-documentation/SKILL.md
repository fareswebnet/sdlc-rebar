---
name: sdlc-documentation
description: Create and maintain repo-first docs: onboarding guides, API docs, ADRs, runbooks, stale-doc checks. Use when documenting a project, onboarding developers, or making SDLC artifacts living.
---

# SDLC Documentation

## Purpose

Keep knowledge close to the work and useful under pressure.

## Workflow

1. Define documentation audiences: developers, product, operators, support, users, auditors, and investors.
2. Keep docs short, linked, versioned, and tied to code/specs/decisions.
3. Create onboarding, API, architecture, runbook, release, and user documentation as needed.
4. Detect stale docs by comparing claims to repo, tests, configs, and production behavior.
5. Prefer repo-first documentation for engineering truth.

## Outputs

- Primary artifacts: `docs/README.md, docs/engineering/developer-onboarding.md, docs/operations/runbooks/, docs/architecture/adr/`.

## Guardrails

- Do not create documents without owner, audience, update trigger, and link to the relevant artifact or code.
