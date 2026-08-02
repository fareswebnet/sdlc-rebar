# Hermes Nightly Follow-Up Prompt

Use this after the feature reaches a preview or production-controlled state.

```text
Run the ReleasePilot Signal Clustering follow-up loop.

Inputs:
- latest PR status
- CI status
- feature flag state
- observability notes
- support or product signals approved for review
- docs/operations/observability.md
- docs/product/analytics/experiments.md
- docs/governance/decision-log.md

Report:
1. What changed since the last check.
2. Which gates are blocked.
3. Which human decision is needed next.
4. Whether the feature flag state is still correct.
5. Whether any incident, support note, or analytics signal should create a product follow-up.
6. Whether any skill should be improved, with evidence.

Do not modify production, secrets, billing, customer communication, or rollout state.
```
