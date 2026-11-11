# sdlc-accessibility-engineering (compact)

When: Build in accessibility from requirements: WCAG 2.2 target, criteria, keyboard and screen-reader support, assistive-tech testing.

Goal: Make accessibility a tested requirement with evidence, not a late audit.

Steps:
1. Set the target (usually WCAG 2.2 AA) and applicable law or policy; note the assistive technologies and platforms in scope.
2. Add accessibility acceptance criteria to each user story and BDD scenario: keyboard-only completion, focus order and visibility…
3. Build on semantic HTML or native platform controls first; use ARIA only to fill gaps and follow established patterns for custom…
4. Bake rules into the design system: color tokens that meet contrast, focus styles, component states, and documented keyboard…
5. Automate what machines can find (linting, axe-style checks in component and end-to-end tests) and treat them as a floor, since…
6. Run manual checks per release for critical journeys: keyboard only, screen reader on the main platforms, zoom and reflow, reduced…
7. Record conformance per criterion with evidence and known gaps with owners and dates; publish an accessibility statement where…
8. Include people with disabilities in usability testing for high-impact flows.

Never:
- Automated scans passing is not conformance.
- Do not remove focus indicators or rely on color alone.
- ARIA misuse is worse than none; prefer native elements.
- Track known gaps openly with an owner and a date.

Next: `sdlc-ui-design-system` for tokens and components, `sdlc-quality-test-strategy` for test integration.
