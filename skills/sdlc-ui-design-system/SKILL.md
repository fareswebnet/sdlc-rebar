---
name: sdlc-ui-design-system
description: Create UI design system guidance, component inventory, interaction conventions, design tokens, responsive behavior, accessibility rules, visual hierarchy, and implementation-ready UI specifications. Use before building UI-heavy features, dashboards, admin tools, SaaS screens, or reusable frontend components.
---

# SDLC UI Design System

## Purpose

Turn product flows into consistent, accessible, maintainable interfaces.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Inventory existing components, tokens, layout constraints, and interaction patterns.
2. Define component usage, states, variants, density, responsive behavior, and accessibility expectations.
3. Specify forms, tables, dashboards, navigation, modals, toasts, and destructive actions.
4. Align UI copy, hierarchy, and visual emphasis with user intent.
5. Create implementation notes without dictating unnecessary framework details.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/ux/design-system.md, docs/ux/component-inventory.md, docs/ux/accessibility.md`.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not introduce one-off UI patterns when an existing component or convention can serve the workflow.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.

## Source Guidance

Use the repository sourcing docs when deeper background is needed:

- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/market-skill-benchmark.md`
