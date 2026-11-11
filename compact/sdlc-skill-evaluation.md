# sdlc-skill-evaluation (compact)

When: Evaluate skills, agents, and harnesses with repeatable scenarios: baseline run without the skill, run with the skill, score against a rubric, and track regressions across versions.

Goal: Prove that a skill changes behavior for the better, and notice when a change makes it worse.

Steps:
1. Define two to five realistic scenarios per skill, including at least one pressure case (deadline, sunk cost, ambiguous request)…
2. Write a rubric per scenario with observable pass/fail items: artifact produced, gate respected, evidence shown, guardrail kept.
3. Run each scenario without the skill to capture baseline behavior and the rationalizations used; then with the skill.
4. Score both runs by the rubric.
5. Store scenarios and scores next to the skill (`evals/<skill>/`) so changes can be re-run and compared by version.
6. Run the repository checks: `python scripts/validate_suite.py` for structure and `python scripts/sdlc_trace.py` fixtures for…
7. Run `python scripts/run_evals.py --model <model> --runs 3` against any OpenAI-compatible endpoint to compare baseline and…
8. Review trigger quality: confirm descriptions fire on the right requests and not on near misses.

Never:
- Run scenarios on realistic tasks, not on the skill text itself.
- Do not tune a skill to pass one scenario while worsening the others; re-run all scenarios.
- Record model and date; results are not portable across models without rechecking.
- A skill that cannot show a measurable benefit should be removed.

Next: `sdlc-skill-evaluation` to apply the fixes, `sdlc-agent-context-engineering` when the problem is context rather than the skill.
