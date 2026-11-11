# sdlc-skill-authoring (compact)

When: Create or revise agent skills with a test-first approach: observe baseline agent failures without the skill, write a minimal skill that addresses them, close loopholes found in pressure scenarios, and keep descriptions…

Goal: Make skills that agents actually follow, by treating skill writing like TDD for process documentation.

Steps:
1. RED: run a realistic scenario without the skill and record the failure and the exact rationalizations the agent used.
2. Write the smallest `SKILL.md` that addresses those failures.
3. Structure the body: purpose, depth levels, workflow, inputs, outputs, guardrails; use flowcharts only for non-obvious decisions…
4. GREEN: rerun the scenario with the skill and confirm compliance.
5. REFACTOR: add pressure scenarios (time, sunk cost, authority), capture new excuses, and add explicit counters until the skill…
6. Keep it lean: move heavy references to separate files, one excellent example beats many, and cut anything that does not change…
7. Register the skill in `data/skills.csv`, the README table, the validator count, and the relevant agent or harness, then run…

Never:
- No skill without an observed failure it addresses.
- Do not duplicate an existing skill; extend or route to it.
- Do not copy third-party skill text; adapt the idea and cite it in `docs/references/`.
- Skill descriptions are routing text; keep them specific and under the size where they stay readable.

Next: `sdlc-skill-evaluation` to prove the skill works before it ships.
