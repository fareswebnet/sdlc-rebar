---
name: sdlc-skill-evaluation
description: Evaluate skills with repeatable scenarios: baseline vs with-skill runs, rubric scoring, regression tracking. Use before publishing or changing a skill, or when one seems ignored or harmful.
---

# SDLC Skill Evaluation

## Purpose

Prove that a skill changes behavior for the better, and notice when a change makes it worse.

## Workflow

1. Define two to five realistic scenarios per skill, including at least one pressure case (deadline, sunk cost, ambiguous request) and one case where the skill should not trigger.
2. Write a rubric per scenario with observable pass/fail items: artifact produced, gate respected, evidence shown, guardrail kept.
3. Run each scenario without the skill to capture baseline behavior and the rationalizations used; then with the skill.
4. Score both runs by the rubric. Keep a skill only if it improves the score or prevents a recorded failure; otherwise simplify or delete it.
5. Store scenarios and scores next to the skill (`evals/<skill>/`) so changes can be re-run and compared by version.
6. Run the repository checks: `python scripts/validate_suite.py` for structure and `python scripts/sdlc_trace.py` fixtures for traceable artifacts.
7. Run `python scripts/run_evals.py --model <model> --runs 3` against any OpenAI-compatible endpoint to compare baseline and with-skill scores, and add your scenarios under `evals/`.
8. Review trigger quality: confirm descriptions fire on the right requests and not on near misses.

## Outputs

- Primary artifacts: `evals/<skill>/scenarios.md` with rubric and baseline-versus-skill scores, change notes per version.

## Guardrails

- Run scenarios on realistic tasks, not on the skill text itself.
- Do not tune a skill to pass one scenario while worsening the others; re-run all scenarios.
- Record model and date; results are not portable across models without rechecking.
- A skill that cannot show a measurable benefit should be removed.

## Handoff

`sdlc-skill-evaluation` to apply the fixes, `sdlc-agent-context-engineering` when the problem is context rather than the skill.

## Provenance

Original to this suite; informed by the Superpowers 'TDD for skills' idea, extended into rubric-scored baseline-versus-skill evaluation. Provenance is tracked in `docs/references/method-sources.md`.
