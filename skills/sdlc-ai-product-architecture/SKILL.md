---
name: sdlc-ai-product-architecture
description: Design AI, LLM, RAG, prompt, context, agent tooling, evaluation, safety, observability, cost, permissions, and human oversight architecture for AI-enabled products. Use when a product includes assistants, copilots, extraction, classification, RAG, autonomous tools, or LLM workflows.
---

# SDLC AI Product Architecture

## Purpose

Make AI product behavior measurable, governable, and safe enough for the use case.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Define AI tasks, success criteria, non-goals, failure modes, and human oversight needs.
2. Design prompts, context, memory, retrieval, tools, permissions, and output constraints.
3. Create evaluation datasets, golden examples, risk tests, and regression checks.
4. Review prompt injection, data leakage, unsafe actions, bias, hallucination, and expensive mistakes.
5. Instrument quality, latency, cost, feedback, and safety signals.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/ai/ai-product-requirements.md, docs/ai/rag-architecture.md, docs/ai/evaluation-plan.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not ship AI behavior whose quality is only judged by it looks good in a demo.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
