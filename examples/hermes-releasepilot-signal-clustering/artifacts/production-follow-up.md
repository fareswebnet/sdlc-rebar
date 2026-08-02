# Production Follow-Up Plan

This plan starts after a real PR is merged and a human release owner approves rollout.

## Daily Hermes Brief

Cadence: every weekday morning during preview.

Report:

- open PRs touching Signal Clustering
- failed CI checks
- blocked gates
- flag state by environment
- new incidents or support notes mentioning clustering
- next required human decision

## Post-Merge Check

Trigger: after merge to main.

Hermes should verify:

- release notes mention the feature flag
- rollback notes exist
- observability dashboard exists or the gap is recorded
- production flag remains disabled until go decision
- docs and BDD scenarios are linked from the PR

## Preview Learning

Track during internal preview:

- clusters accepted by product reviewers
- clusters rejected by product reviewers
- clusters split or merged manually
- average spec draft edit distance
- time from signal batch to accepted spec
- reviewer comments about confidence explanation

## ROI Review

Cadence: weekly.

Compute:

- agent run cost
- human review time
- cycle time from idea to PR
- PR rework rate
- defect escape rate
- spec edit rate
- percentage of generated specs accepted

Decision:

- keep workflow as is
- tighten a gate
- improve a skill
- reduce autonomy
- expand automation to a connector

## Skill Improvement Loop

Hermes may propose a skill update when the same failure appears at least twice, such as:

- BDD examples missing tenant isolation
- PR body omitting rollback
- reviewers rejecting low-confidence explanations
- generated specs losing evidence links

Skill updates require human review before becoming durable project behavior.
