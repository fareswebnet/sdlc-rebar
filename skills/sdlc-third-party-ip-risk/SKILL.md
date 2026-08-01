---
name: sdlc-third-party-ip-risk
description: Review third-party dependencies, open-source licenses, IP risk, AI-generated code policy, vendor lock-in, SBOM, provenance, dependency health, commercial SaaS reliance, and due diligence readiness. Use before release, fundraising, enterprise sales, major dependency adoption, or supply-chain review.
---

# SDLC Third Party IP Risk

## Purpose

Make external code, services, models, and licenses visible before they become due diligence problems.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Inventory dependencies, vendors, APIs, models, datasets, tools, and copied/generated code sources.
2. Review license compatibility, attribution, redistribution obligations, security posture, and maintenance health.
3. Assess vendor lock-in, data portability, exit plan, pricing exposure, and operational criticality.
4. Define policy for AI-generated code, snippets, datasets, prompts, and embeddings.
5. Produce a risk register and evidence pack for diligence.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/risk/third-party-register.md, docs/risk/license-review.md, docs/risk/ai-generated-code-policy.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not add critical third-party dependencies without ownership, license, security, exit, and cost review.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
