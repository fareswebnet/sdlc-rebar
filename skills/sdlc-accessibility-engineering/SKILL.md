---
name: sdlc-accessibility-engineering
description: Engineer accessibility in from requirements: target a WCAG 2.2 level, write accessibility acceptance criteria, build with semantic structure and keyboard and screen-reader support, test automatically and manually with assistive technology, and track conformance. Use for any UI work, public-sector or regulated products, design system changes, or before release of user-facing flows.
---

# SDLC Accessibility Engineering

## Purpose

Make accessibility a tested requirement with evidence, not a late audit.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Set the target (usually WCAG 2.2 AA) and applicable law or policy; note the assistive technologies and platforms in scope.
2. Add accessibility acceptance criteria to each user story and BDD scenario: keyboard-only completion, focus order and visibility, labels and error messages, contrast, text resize and reflow, target size, motion and timing controls.
3. Build on semantic HTML or native platform controls first; use ARIA only to fill gaps and follow established patterns for custom widgets.
4. Bake rules into the design system: color tokens that meet contrast, focus styles, component states, and documented keyboard behavior per component.
5. Automate what machines can find (linting, axe-style checks in component and end-to-end tests) and treat them as a floor, since they catch only part of the problems.
6. Run manual checks per release for critical journeys: keyboard only, screen reader on the main platforms, zoom and reflow, reduced motion, and forms with errors.
7. Record conformance per criterion with evidence and known gaps with owners and dates; publish an accessibility statement where required.
8. Include people with disabilities in usability testing for high-impact flows.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `docs/ux/accessibility.md`, acceptance criteria in specs, automated checks in CI, conformance report with gaps.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Automated scans passing is not conformance.
- Do not remove focus indicators or rely on color alone.
- ARIA misuse is worse than none; prefer native elements.
- Track known gaps openly with an owner and a date.

## Handoff

`sdlc-ui-design-system` for tokens and components, `sdlc-quality-test-strategy` for test integration.

## Source Guidance

Original to this suite; informed by WCAG 2.2 and accessible engineering practice. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
