---
name: sdlc-security-privacy-compliance
description: Integrate secure SDLC, threat modeling, privacy, compliance, abuse cases, security requirements, secure architecture, secure coding review, secrets/config review, data protection, and release security gates. Use when designing or reviewing features with sensitive data, auth, payments, AI, fintech, healthcare, B2B, or regulatory exposure.
---

# SDLC Security Privacy Compliance

## Purpose

Build security and privacy into the SDLC before release pressure hides risk.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Identify assets, actors, trust boundaries, abuse cases, compliance triggers, and sensitive data.
2. Define security and privacy requirements alongside product requirements.
3. Review architecture, code, dependencies, secrets, logging, and operational controls.
4. Map risks to mitigations, owners, acceptance criteria, and release gates.
5. Escalate legal/accounting/compliance uncertainty as non-advice requiring qualified review.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/security/threat-model.md, docs/security/security-requirements.md, docs/security/privacy-review.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not treat this skill as legal, accounting, financial, or investment advice.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
