# Example - Agent Factory Idea To PR

This example shows how the agent-factory layer can turn a raw app idea into a reviewable simulated PR.

## Raw App Idea

ReleasePilot is a B2B SaaS app for small product-engineering teams. It reads a feature brief, acceptance criteria, CI status, risk notes, and deployment context, then produces a release-readiness view with missing gates, rollback notes, and post-release checks.

The first vertical slice is intentionally narrow:

- create a release checklist from a feature brief
- classify missing readiness gates
- show a release risk summary
- export a PR-ready validation summary

## Target User

Founder-CTO or engineering lead in a 3-20 person team that ships frequently but lacks formal release management.

## Harness

Use `harnesses/app-idea-to-production.yaml`.

Stop at PR readiness. Do not deploy to production.

## Runtime Prompt

Use one of the prompts in `prompts/`:

- `prompts/codex.md`
- `prompts/claude-code.md`
- `prompts/hermes.md`

## Generated Artifacts

| Artifact | Purpose |
|---|---|
| `artifacts/task-graph.yaml` | Agent routing, stages, gates, and stop conditions. |
| `artifacts/sdlc-artifact-map.md` | Expected product, BDD, architecture, test, and release artifacts. |
| `artifacts/simulated-pr.md` | Example PR body produced by the pipeline. |
| `artifacts/review-gate.md` | Example merge-gate review output. |

## Expected Flow

1. `orchestrator` classifies the request as greenfield MVP with high automation and production stop.
2. `product-strategist` writes the product brief and MVP scope.
3. `domain-architect` creates domain rules, bounded contexts, and BDD examples.
4. `ux-ui-designer` defines the core release dashboard states.
5. `solution-architect` chooses a small modular architecture and data model.
6. `fullstack-builder` implements the first vertical slice in an isolated branch or worktree.
7. `qa-test-engineer` maps acceptance examples to tests.
8. `security-reviewer` checks auth, tenant isolation, dependency, and data risk.
9. `code-reviewer` produces the merge decision.
10. `release-manager` prepares the release notes but stops before deployment.

## Human Gates

- Approve MVP scope before architecture.
- Approve architecture and data ownership before implementation.
- Approve dependency additions before installation.
- Approve production deployment separately; this example stops before that gate.

## Success Criteria

- The PR explains user behavior, architecture impact, tests, and residual risk.
- The first slice is small enough for one agent-run implementation.
- Validation maps back to BDD examples.
- The release checklist can be inspected by a human before merge.
