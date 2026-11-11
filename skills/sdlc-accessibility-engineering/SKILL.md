---
name: sdlc-accessibility-engineering
description: Build in accessibility from requirements: WCAG 2.2 target, criteria, keyboard and screen-reader support, assistive-tech testing. Use for UI work, regulated products, or design system changes.
---

# SDLC Accessibility Engineering

## Purpose

Make accessibility a tested requirement with evidence, not a late audit.

## Workflow

1. Set the target (usually WCAG 2.2 AA) and applicable law or policy; note the assistive technologies and platforms in scope.
2. Add accessibility acceptance criteria to each user story and BDD scenario: keyboard-only completion, focus order and visibility, labels and error messages, contrast, text resize and reflow, target size, motion and timing controls.
3. Build on semantic HTML or native platform controls first; use ARIA only to fill gaps and follow established patterns for custom widgets.
4. Bake rules into the design system: color tokens that meet contrast, focus styles, component states, and documented keyboard behavior per component.
5. Automate what machines can find (linting, axe-style checks in component and end-to-end tests) and treat them as a floor, since they catch only part of the problems.
6. Run manual checks per release for critical journeys: keyboard only, screen reader on the main platforms, zoom and reflow, reduced motion, and forms with errors.
7. Record conformance per criterion with evidence and known gaps with owners and dates; publish an accessibility statement where required.
8. Include people with disabilities in usability testing for high-impact flows.

## Outputs

- Primary artifacts: `docs/ux/accessibility.md`, acceptance criteria in specs, automated checks in CI, conformance report with gaps.

## Guardrails

- Automated scans passing is not conformance.
- Do not remove focus indicators or rely on color alone.
- ARIA misuse is worse than none; prefer native elements.
- Track known gaps openly with an owner and a date.

## Handoff

`sdlc-ui-design-system` for tokens and components, `sdlc-quality-test-strategy` for test integration.

## Provenance

Original to this suite; informed by WCAG 2.2 and accessible engineering practice. Provenance is tracked in `docs/references/method-sources.md`.
