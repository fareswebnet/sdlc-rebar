# Agent Runtime Matrix

This matrix separates stable SDLC method from runtime-specific execution.

## Principle

- Skills define the method and expected artifacts.
- Agents define role, permissions, gates, and handoffs.
- Harnesses define the state machine.
- Runtime adapters explain how to execute the same system in Codex, Claude Code, Hermes, OpenClaw, CI, or a custom orchestrator.

## Runtime Fit

| Runtime | Best role | Fit | Watch-outs |
|---|---|---|---|
| Codex | Repo execution, review, worktrees, skills, hooks, scripted runs | Strong for idea-to-PR and quality gates | Keep production commands approval-gated and avoid overloading global instructions |
| Claude Code | Terminal coding agent, repo edits, MCP-connected tools | Strong for implementation and repo-local workflows | Keep `CLAUDE.md` concise and permission modes explicit |
| Hermes | Long-running orchestrator, memory, schedules, subagents, provider routing | Strong for autonomous project loops and follow-up automation | Treat generated plans as proposals until gates pass |
| OpenClaw | Workspace assistant and skill adapter | Useful for experimentation and MCP-mediated Claude Code control | Keep GitHub and repo artifacts as source of truth |
| GitHub Actions | Deterministic CI, scheduled checks, branch protection | Strong for repeatable gates and reports | Avoid giving CI broad write or production authority |
| Custom Agents SDK | Productized orchestration, handoffs, traceability, app-specific controls | Strong when building a reusable platform | Requires engineering investment and explicit safety design |

## Agent To Runtime Defaults

| Agent | Primary runtime | Secondary runtime | Typical mode |
|---|---|---|---|
| `orchestrator` | Hermes | Codex | supervised planning and routing |
| `product-strategist` | Codex | Hermes | advisory research and docs |
| `domain-architect` | Codex | Claude Code | advisory modeling and BDD |
| `ux-ui-designer` | Codex | Claude Code | design specs and frontend validation |
| `solution-architect` | Codex | Claude Code | architecture and data decisions |
| `fullstack-builder` | Codex | Claude Code | bounded repo edits |
| `qa-test-engineer` | Codex | Claude Code | tests and regression checks |
| `security-reviewer` | Codex | Claude Code | read-first review and targeted fixes |
| `devops-sre` | Codex | Hermes | release, telemetry, and runbooks |
| `code-reviewer` | Codex | Claude Code | merge gate review |
| `release-manager` | Hermes | Codex | rollout, approvals, and follow-up |
| `legacy-analyst` | Codex | Claude Code | registry, rule matrices, convergence classification |
| `independent-verifier` | Claude Code | Codex | separate-context audit and visas |

## Required Human Gates

- Product scope and strategic tradeoffs.
- Architecture decisions that create long-term coupling.
- Dependency additions and license risk.
- Secrets, credentials, payments, customer data, and privacy.
- Destructive migrations and production deployment.
- Compliance, legal, accounting, or regulated-domain claims.
