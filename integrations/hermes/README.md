# Hermes Integration

Use Hermes as an orchestration layer when the project needs long-running autonomy, scheduled follow-up, subagents, memory, provider routing, and delegated coding.

## Fit

Hermes is a good runtime for:

- routing a project through the harnesses
- spawning isolated implementation and review workstreams
- scheduling production feedback loops
- delegating coding to Codex or Claude Code skills when configured
- keeping long-running project memory outside a single coding session

## Install Skills

Keep this repository as a project dependency and expose the `skills/`, `agents/`, `harnesses/`, and `pipelines/` folders as project context. If the local Hermes setup supports skill folders, mirror each `skills/sdlc-*` directory into the configured Hermes skills path.

## Example Runs

Interactive project kickoff:

```bash
hermes chat --worktree --skills sdlc-delivery-system \
  -q "Use harnesses/app-idea-to-production.yaml for this app idea. Create the product, BDD, architecture, and implementation plan. Stop before coding until the plan is reviewable."
```

Parallel implementation slice:

```bash
hermes chat --worktree --skills sdlc-code-change-execution \
  -q "Use agents/fullstack-builder.yaml. Implement slice 1 from docs/engineering/implementation-plan.md, run tests, and prepare a PR summary."
```

Production learning report:

```bash
hermes chat --skills sdlc-incident-support-feedback,sdlc-product-analytics-experimentation \
  -q "Run pipelines/production-feedback-loop.md against the latest support and observability signals available through approved tools."
```

Complete ReleasePilot example:

```bash
python3 examples/hermes-releasepilot-signal-clustering/scripts/validate_hermes_example.py

hermes chat --worktree --skills sdlc-delivery-system,sdlc-ai-assisted-development,sdlc-bdd-specifications,sdlc-quality-test-strategy \
  -q "$(cat examples/hermes-releasepilot-signal-clustering/prompts/hermes-kickoff.md)"
```

The full example lives in `examples/hermes-releasepilot-signal-clustering/` and shows how Hermes can coordinate product framing, bounded contexts, BDD, TDD red tests, scoped implementation, security review, PR review, feature flags, observability, and ROI follow-up.

## Recommended Orchestration

- `orchestrator` owns the task graph.
- `product-strategist`, `domain-architect`, `solution-architect`, and `ux-ui-designer` run before implementation.
- `fullstack-builder` runs in isolated worktrees.
- `qa-test-engineer`, `security-reviewer`, and `code-reviewer` run independently.
- `release-manager` owns go/no-go and post-release follow-up.

## Safety Defaults

- keep GitHub issues, branches, PRs, and checks as the source of truth
- do not let long-running memory override repo artifacts
- require human approval for production, secrets, migrations, dependency additions, and customer-impacting communication
