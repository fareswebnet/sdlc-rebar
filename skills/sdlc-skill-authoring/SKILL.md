---
name: sdlc-skill-authoring
description: Create or revise agent skills with a test-first approach: observe baseline agent failures without the skill, write a minimal skill that addresses them, close loopholes found in pressure scenarios, and keep descriptions trigger-focused. Use when adding a skill to this suite, tightening a skill that agents ignore, or reviewing contributions.
---

# SDLC Skill Authoring

## Purpose

Make skills that agents actually follow, by treating skill writing like TDD for process documentation.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. RED: run a realistic scenario without the skill and record the failure and the exact rationalizations the agent used.
2. Write the smallest `SKILL.md` that addresses those failures. Frontmatter has only `name` and `description`; the description states when to use the skill, not how it works, so agents do not follow the summary instead of the body.
3. Structure the body: purpose, depth levels, workflow, inputs, outputs, guardrails; use flowcharts only for non-obvious decisions and tables for quick reference.
4. GREEN: rerun the scenario with the skill and confirm compliance.
5. REFACTOR: add pressure scenarios (time, sunk cost, authority), capture new excuses, and add explicit counters until the skill holds.
6. Keep it lean: move heavy references to separate files, one excellent example beats many, and cut anything that does not change behavior.
7. Register the skill in `data/skills.csv`, the README table, the validator count, and the relevant agent or harness, then run `python scripts/validate_suite.py`.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: New or revised `skills/sdlc-*/SKILL.md` with `agents/openai.yaml`, scenario notes, and a passing validator run.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- No skill without an observed failure it addresses.
- Do not duplicate an existing skill; extend or route to it.
- Do not copy third-party skill text; adapt the idea and cite it in `docs/references/`.
- Skill descriptions are routing text; keep them specific and under the size where they stay readable.

## Handoff

`$sdlc-skill-evaluation` to prove the skill works before it ships.

## Source Guidance

Adapted idea, extended beyond the source, not copied text: superpowers writing-skills (TDD for skills, description discipline). Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
