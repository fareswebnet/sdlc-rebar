---
name: sdlc-delivery-system
description: End-to-end product-tech SDLC orchestrator for moving from idea, discovery, PRD, domain modeling, BDD, architecture, backlog, implementation, tests, release, observability, support feedback, and continuous improvement. Use when starting a project, auditing an existing delivery flow, choosing which sdlc-* skill to run next, or scaffolding repo-first SDLC artifacts.
---

# SDLC Delivery System

## Purpose

Coordinate the complete SDLC without turning it into bureaucracy.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Classify the work as greenfield, feature, refactor, incident, audit, or production improvement.
2. Select Lean, Standard, or Enterprise-ready depth based on team size, regulation, risk, and maturity.
3. Route to the smallest set of specialized sdlc-* skills needed for the current decision.
4. Keep a traceability chain from idea to requirements, BDD examples, architecture, tickets, tests, release, and production metrics.
5. When the user wants automation, select the smallest relevant harness from `harnesses/`: app idea to production, feature to production, or production feedback loop.
6. Use `agents/` role files to assign bounded specialist work with permissions, gates, and handoffs.
7. Use the scaffold script when the target repo needs the standard docs tree.
8. For spec-driven work, run the chain in order and skip steps only with a stated reason: `sdlc-project-constitution` once per repo, then `sdlc-design-brainstorming`, `sdlc-spec-clarification`, `sdlc-requirements-checklist`, `sdlc-implementation-planning`, `sdlc-task-breakdown`, `sdlc-cross-artifact-analysis`.
9. For execution, require `sdlc-branch-worktree-lifecycle` for isolation, `sdlc-test-driven-development` for behavior changes, `sdlc-systematic-debugging` for failures, `sdlc-subagent-driven-execution` for multi-task plans, and `sdlc-verification-before-completion` before any done claim.
10. Make traceability executable with `sdlc-traceability-ledger` and `python scripts/sdlc_trace.py`, and close tasks only against `sdlc-definition-of-done`. Pick step depth from `docs/references/depth-matrix.md`; for the full chain use `harnesses/spec-driven-delivery.yaml`.
11. For legacy replacement or merging two systems, switch to `sdlc-migration-batch-orchestration` and `sdlc-system-merge-convergence`, run `harnesses/legacy-migration.yaml` or `harnesses/system-merge.yaml`, and measure progress only against the frozen registry.
12. After a build pass, run `sdlc-spec-convergence` to append remaining work, and `sdlc-code-review-reception` when feedback arrives.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/governance/decision-log.md, docs/governance/risk-register.md, docs/delivery/roadmap.md, docs/delivery/production-readiness.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.
- Optional automation route through `agents/`, `harnesses/`, `pipelines/`, and `integrations/` when the user wants autonomous or semi-autonomous execution.

## Guardrails

- Do not start coding until the expected behavior, affected architecture/data boundaries, tests, and validation path are explicit.
- Do not delegate production deployment, secrets, destructive migrations, customer data, payments, or customer-facing communication without explicit human approval.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
- `docs/references/agent-runtime-matrix.md`

## Extra

To scaffold standard documentation in a repo, run `python skills/sdlc-delivery-system/scripts/scaffold_sdlc_docs.py --target /path/to/repo` from this suite.

For automated execution, start with:

- `harnesses/app-idea-to-production.yaml`
- `harnesses/feature-to-production.yaml`
- `harnesses/production-feedback-loop.yaml`
