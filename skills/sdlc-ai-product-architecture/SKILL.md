---
name: sdlc-ai-product-architecture
description: Design AI, LLM, RAG, prompt, context, agent tooling, evaluation, safety, observability, cost, permissions, and human oversight architecture for AI-enabled products. Use when a product includes assistants, copilots, extraction, classification, RAG, autonomous tools, or LLM workflows.
---

# SDLC AI Product Architecture

## Purpose

Make AI product behavior measurable, governable, and safe enough for the use case.

## Workflow

1. Define AI tasks, success criteria, non-goals, failure modes, and human oversight needs.
2. Design prompts, context, memory, retrieval, tools, permissions, and output constraints.
3. Create evaluation datasets, golden examples, risk tests, and regression checks.
4. Review prompt injection, data leakage, unsafe actions, bias, hallucination, and expensive mistakes.
5. Instrument quality, latency, cost, feedback, and safety signals.

## Outputs

- Primary artifacts: `docs/ai/ai-product-requirements.md, docs/ai/rag-architecture.md, docs/ai/evaluation-plan.md`.

## Guardrails

- Do not ship AI behavior whose quality is only judged by it looks good in a demo.
