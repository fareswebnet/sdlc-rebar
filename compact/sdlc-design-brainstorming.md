# sdlc-design-brainstorming (compact)

When: Turn a rough idea or feature request into an approved design via dialogue: one question at a time, compare approaches, get explicit approval before planning or code.

Goal: Prevent building the wrong thing by making design approval a hard gate, scaled to the size of the change.

Steps:
1. Explore the project first: existing docs, recent commits, constraints, similar features, and conventions.
2. If the request spans several independent subsystems, say so and decompose into separate specs before refining details.
3. Ask clarifying questions one at a time, preferring multiple choice, focused on purpose, constraints, and success criteria.
4. Propose two or three approaches with trade-offs and a recommendation, and apply YAGNI: remove features that are not needed to…
5. Present the design in sections sized to their complexity (architecture, components, data flow, error handling, testing) and…
6. Write the approved design to `docs/product/` or the feature spec folder, self-review it for ambiguity, contradictions, and scope…
7. Only after approval, hand off to `sdlc-implementation-planning` or `sdlc-task-breakdown`; never jump straight to code.

Never:
- Hard gate: no implementation, scaffolding, or code until the user approves the design.
- A small change gets a short design, not a skipped one.
- In existing code, follow current structure; propose targeted improvements only where they affect the work.
- Keep each design unit understandable and testable in isolation, with clear interfaces.

Next: `sdlc-spec-clarification` for gaps, then `sdlc-implementation-planning`.
