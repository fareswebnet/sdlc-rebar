---
name: sdlc-api-integration-contracts
description: Define API, event, webhook, file, and third-party integration contracts using OpenAPI, AsyncAPI, schemas, versioning, idempotence, retries, errors, compatibility, and contract testing. Use before integrating services, exposing public APIs, adding events, or changing external contracts.
---

# SDLC API Integration Contracts

## Purpose

Prevent hidden coupling and integration ambiguity.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Identify producers, consumers, ownership, protocols, auth, data classification, and compatibility needs.
2. Specify request/response, event, webhook, error, retry, pagination, and idempotency behavior.
3. Version contracts and document deprecation policy.
4. Map contracts to bounded contexts, tests, observability, and support impact.
5. Generate or update OpenAPI/AsyncAPI skeletons when useful.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/architecture/api-contracts.md, docs/architecture/event-catalog.md, docs/quality/contract-tests.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not change a contract without naming impacted consumers and compatibility behavior.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
