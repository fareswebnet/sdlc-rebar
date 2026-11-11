---
name: sdlc-ci-cd-platform
description: Design the delivery platform: CI/CD pipelines, security scans, artifact provenance, environments, secrets, IaC. Use when setting up or improving pipelines or deployment automation.
---

# SDLC DevOps CI CD Platform

## Purpose

Make build, test, preview, and deploy boring enough for fast teams.

## Workflow

1. Inventory local setup, dependencies, scripts, env vars, services, and onboarding friction.
2. Design pipeline stages for build, lint, typecheck, tests, security, artifacts, and deploy.
3. Define environment strategy: local, preview, staging, production, data, secrets, and isolation.
4. Add supply-chain controls appropriate to risk: lockfiles, provenance, SBOM, pinned actions, permissions.
5. Measure developer experience and DORA-relevant flow.

## Outputs

- Primary artifacts: `docs/delivery/ci-cd-platform.md, docs/delivery/environment-strategy.md, docs/engineering/developer-onboarding.md`.

## Guardrails

- Do not add deployment automation without a rollback and secrets strategy.
