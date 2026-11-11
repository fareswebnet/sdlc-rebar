# Example - Hermes ReleasePilot Signal Clustering

This example turns the Hermes case study into a concrete agent-factory run for a product feature.

ReleasePilot is a B2B SaaS product that helps product-engineering teams convert customer feedback, support tickets, product signals, and production incidents into prioritized decisions, verifiable specs, engineering tickets, assisted PRs, release notes, and post-release learning.

The feature in this example is `Signal Clustering`:

- group similar feedback items into actionable clusters
- propose a product priority with confidence and evidence
- require human validation before creating an engineering spec
- generate BDD scenarios, red tests, implementation tasks, PR evidence, release notes, telemetry, and ROI follow-up

## What This Example Implements

This is not only a prompt. It is a complete Hermes operating pack for one feature:

| Area | Files |
|---|---|
| Hermes project context | `hermes/.hermes.md`, `hermes/profile.releasepilot.yaml`, `hermes/memory-seed.md` |
| Project-specific skills | `skills/releasepilot-*/SKILL.md` |
| Runtime prompts | `prompts/hermes-kickoff.md`, `prompts/hermes-stage-handoff.md`, `prompts/hermes-nightly-followup.md` |
| Delivery artifacts | `artifacts/task-graph.yaml`, `artifacts/signal-clustering-sdlc-map.md`, `artifacts/bdd-scenarios.feature`, `artifacts/red-tests.md`, `artifacts/feature-flag.yaml`, `artifacts/implementation-plan.md`, `artifacts/simulated-pr.md`, `artifacts/review-gate.md`, `artifacts/production-follow-up.md` |
| Local verification | `scripts/validate_hermes_example.py` |

## Operating Model

Hermes acts as the orchestration layer, not the only coding agent.

Recommended split:

| Responsibility | Runtime |
|---|---|
| Orchestration, memory, checkpoints, scheduling, subagent routing | Hermes |
| Repo-local implementation and diff work | Codex, Claude Code, or Hermes worktree subagent |
| Independent review | Codex, Claude Code, or separate Hermes review subagent |
| Source of truth | GitHub issues, branches, PRs, CI checks, versioned docs |

The point is to make engineering judgment executable:

`idea -> product intent -> domain model -> BDD -> architecture -> red tests -> implementation -> green tests -> review -> release readiness -> production learning`

## Quick Run

From a real ReleasePilot repository, copy or reference this folder as agent context, then start Hermes with the dedicated profile:

```bash
hermes --profile releasepilot
```

Kick off the run:

```bash
hermes chat --worktree --skills sdlc-delivery-orchestrator,sdlc-ai-coding-governance,sdlc-bdd-specifications,sdlc-test-strategy \
  -q "$(cat examples/hermes-releasepilot-signal-clustering/prompts/hermes-kickoff.md)"
```

If your Hermes installation supports project-local skills, expose the example skills as project skills. If not, attach them as context files in the kickoff prompt.

## Human Gates

Hermes must stop for explicit human approval before:

- validating MVP scope
- accepting BDD examples as the contract
- accepting the ADR and data ownership
- adding dependencies
- writing or running migrations
- touching customer data
- enabling the feature flag outside local or preview
- sending customer-facing communication
- deploying to production

## Success Criteria

The run is successful when it produces:

- a small approved vertical slice
- BDD scenarios accepted before implementation
- red tests written before production code
- implementation constrained to the Signal Clustering module
- feature flag and rollout owner recorded
- validation commands and evidence
- security and privacy review
- PR summary and merge gate
- post-release telemetry and ROI follow-up plan

## Verify This Example

From this repository:

```bash
python3 examples/hermes-releasepilot-signal-clustering/scripts/validate_hermes_example.py
```

The repository-wide validator also checks that the core files are present:

```bash
python3 scripts/validate_suite.py
```

## Limits

This example is a delivery-system artifact. It is not legal, compliance, investment, accounting, or security certification advice. Regulated or high-impact deployments need qualified human review and organization-specific controls.
