# Pipeline: Idea To PR

Use this pipeline when the user arrives with a raw app idea and expects the agent system to produce a reviewed implementation branch or pull request.

## Outcome

Produce a PR or equivalent branch with:

- product brief and PRD
- BDD examples and traceability
- architecture, data, and API decisions
- implementation plan
- code changes and tests
- validation evidence
- review findings and residual risk

## Sequence

1. Run `product-strategist` to turn the raw idea into a product brief, MVP scope, and PRD.
2. Run `domain-architect` to define ubiquitous language, bounded contexts, and BDD examples.
3. Run `ux-ui-designer` to define journeys, screens, UI states, accessibility, and tracking.
4. Run `solution-architect` to define architecture, data ownership, contracts, identity, and deployment constraints.
5. Run `orchestrator` to split the implementation into vertical slices with gates.
6. Run one or more `fullstack-builder` agents in isolated branches or worktrees.
7. Run `qa-test-engineer` against the changed behavior and regression risks.
8. Run `security-reviewer` for security, privacy, dependency, and tenant-isolation risk.
9. Run `code-reviewer` to decide whether the change can merge.

## Gates

- Do not implement until behavior, boundaries, tests, and rollback expectations are explicit.
- Do not add new dependencies unless the dependency choice is approved and recorded.
- Do not merge until validation evidence exists or residual risk is accepted.
- Do not deploy to production from this pipeline; hand off to `pr-to-production.md`.

## Runtime Hints

- Codex: use a worktree or `codex exec` in `workspace-write` for scripted stages.
- Claude Code: keep `CLAUDE.md` short and project-specific, then run bounded tasks per branch.
- Hermes: use `hermes chat --worktree --skills <skill>` for delegated implementation tasks.
- OpenClaw: use workspace skills as an adapter, with GitHub remaining the source of truth.
