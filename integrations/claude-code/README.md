# Claude Code Integration

Use Claude Code as a terminal coding agent for repo-local execution, implementation, tests, and MCP-connected workflows.

## Install Skills

Use the installer, which puts skills in `.claude/skills` of the target repo:

```bash
python scripts/install.py --runtime claude --target /path/to/repo --agents-md --with-kit --native-roles
```

Or install this repository as a plugin through its marketplace (`.claude-plugin/marketplace.json`). Invoke a skill with `/sdlc-<name>` or let it trigger from its description.

## Project Memory

The single memory file is `AGENTS.md`; `--agents-md` maintains a managed block in it. If your Claude Code version only reads `CLAUDE.md`, create a one-line `CLAUDE.md` containing `@AGENTS.md` rather than duplicating content. The block looks like:

```md
Use the AI SDLC suite as the delivery method.

Before implementation, produce or update:
- product behavior or BDD examples
- affected architecture, data, API, and security boundaries
- validation commands
- rollback notes

Use the agent role files under `agents/` to decide whether the task is product, domain, architecture, build, QA, security, release, or production feedback work.
```

## Suggested Prompts

```text
Use the role `agents/fullstack-builder.yaml` and the skills `sdlc-implementation-planning` and `sdlc-code-change-execution`.
Implement only the first vertical slice described in docs/engineering/implementation-plan.md.
Run the validation commands and report residual risk.
```

```text
Use the role `agents/code-reviewer.yaml`.
Review the current diff against docs/product/prd.md, docs/product/bdd, and docs/architecture.
Lead with blocking findings and missing tests.
```

## Measured on Claude

`python scripts/run_evals.py --model sonnet --base-url claude-cli --workers 4 --runs 3` uses your local Claude Code CLI (tools, skills, MCP connectors, and settings disabled, so only the scenario prompt and the compact skill apply). Results from 2026-11-11, 16 scenarios, 3 runs each (`evals/results/`):

| Model | Without skill | With compact skill |
|---|---|---|
| Sonnet | 22/48 | 44/48 |
| Haiku | 23/48 | 43/48 |

A first Claude run was invalid: without `--strict-mcp-config` the CLI still exposed claude.ai connectors (Gmail, Docs) to the model, and some replies were tool calls. This is fixed and every prompt now states that no tool access exists.

Where the skills change behavior (baseline 0/3 on both models): independent verification (self-visa), registry before target code, TDD under time pressure, TDD with a fix handed over or "the suite is green" pressure, design approval for a "trivial" change, decomposing a multi-subsystem request, and refusing "Ready for release" on Sonnet when acceptance tests were not run.

Harder cases added for the three that did not discriminate:

- Design gate: `design-small-change-pressure` and `design-decompose-scaffold` discriminate. The original `design-gate` still does not (3/3 without skill).
- TDD for a bug: `tdd-fix-supplied` and `tdd-green-suite-pressure` discriminate (0/3 without skill), `tdd-bug` does not.
- Verification: still does not discriminate. `verify-claim`, `verify-requirements-gap`, `verify-stale-evidence` and `verify-fix-claim-green-test` pass at or near 3/3 without skill; only `verify-delegated-attribution` (Haiku 1/3, Sonnet 2/3 baseline) and Sonnet's `verify-partial-evidence` show a gap. Claude is already reliable at not claiming unverified success, so this skill shows little measurable benefit on these models.

Caveats: string checks are a floor and the sample is small. Several failures with the skill are false negatives (a correct reply that misses the regex wording, e.g. `tdd-fix-supplied`, `design-small-change-pressure`); I did not widen the regexes after the run. The new scenarios were written after observing baseline replies, so their discrimination is partly by construction. Re-run on your own models and prompts.

## Claude Code notes

- Skills with side effects (`sdlc-tasks-to-issues`, `sdlc-cutover-rollback`, `sdlc-data-migration-reconciliation`) set `disable-model-invocation: true`, so they only run when you invoke them explicitly with `/sdlc-<name>`.
- Claude Code shows skill descriptions to the model within a limited budget. The 58 descriptions total about 11,100 characters; if you install many other skills, descriptions may be shortened. Install only the subset you use, or rely on the harnesses and explicit `/sdlc-<name>` calls.
- Subagents: `--native-roles` writes `.claude/agents/*.md`; run the `independent-verifier` role as its own subagent so it does not see the builder's reasoning.

## MCP Connectors

Use MCP for authorized private context:

- GitHub issues, PRs, and checks
- Linear or Jira backlog
- Slack support signal when approved
- observability tools
- read-only databases or warehouses
- docs and design tools

Prefer read-only connectors until the workflow and permission model are stable.

## Safety Defaults

- use planning or read-only mode for architecture, security, and production tasks
- use broader autonomy only in isolated branches or worktrees
- require approval for dependency installation, secrets, migrations, production deploys, payments, and customer data changes
