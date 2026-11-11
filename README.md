# SDLC Rebar

*Reinforcement for AI-driven delivery: evidence, verification, no unproven claims.*

Rebar is poured into your existing delivery process, not in place of it: an agent skill suite (58 `sdlc-*` skills, agent roles, harnesses, evals) for the full product-tech software lifecycle, with independent verification and measured effect.

This repository packages 58 `sdlc-*` skills and optional presets to help a team move from idea to production learning:

`idea -> discovery -> PRD -> domain model -> bounded contexts -> BDD -> UX/UI -> architecture/data -> contracts -> backlog -> implementation -> tests -> release -> observability -> incidents/support -> improvement`

The suite is designed for startups and scale-ups by default, but each skill can be used in Lean, Standard, or Enterprise-ready depth. It now also includes an agent-factory layer for highly automated coding workflows across Codex, Claude Code, Hermes, OpenClaw, GitHub Actions, MCP connectors, or a custom orchestrator.

## What This Is

- A repo-first SDLC operating system for AI-assisted product and engineering work.
- A set of portable agent skills using `SKILL.md` folders.
- A vendor-neutral agent orchestration layer for moving from app idea to PR, preview, release, and production learning.
- A standards-informed implementation layer over ISO/IEC/IEEE, DDD, BDD, OWASP, NIST, SLSA, DORA, OpenTelemetry, SRE, FinOps, WCAG, OpenAPI, AsyncAPI, and AI risk practices.

## What This Is Not

- Not legal, accounting, financial, compliance, investment, or security certification advice.
- Not a replacement for qualified review in regulated or high-risk contexts.
- Not a command to over-document every project. Use the depth that fits the risk.
- Not a license to run production changes, secrets, destructive migrations, payments, or customer-impacting communications without human approval.

## Install

One installer covers every runtime. Skills go where each runtime discovers them, and the only repository memory file is `AGENTS.md` (a managed block that never overwrites your own content).

```bash
python scripts/install.py --runtime codex|claude|antigravity|generic --target /path/to/repo --agents-md --with-kit
python scripts/install.py --runtime codex --scope user        # user-level skills
python scripts/install.py --runtime claude --target . --native-roles   # also .claude/agents subagents
```

| Runtime | Project skills folder | Invocation |
|---|---|---|
| Codex | `.agents/skills` | `$sdlc-<name>` |
| Claude Code | `.claude/skills` (or plugin via `.claude-plugin/`) | `/sdlc-<name>` or by description |
| Antigravity | `.agents/skills` (or plugin via `plugin.json`) | mention the skill name |
| Open-source or other LLM | `.agents/skills`, plus `python scripts/skill_index.py` | name the skill in the prompt |

Small models and runtimes without skills: `compact/` holds shortened skills, `python scripts/sdlc_runner.py` runs a gated loop against any OpenAI-compatible endpoint, and `python scripts/run_evals.py` measures whether a model follows the skills (see `evals/README.md` and `integrations/generic-llm/`).

Restart the agent session so new skills are discovered. Fallbacks for missing tools (subagents, worktrees, MCP) are in `docs/references/runtime-capabilities.md`; per-runtime notes are in `integrations/`.

## Skills

| Skill | Purpose |
|---|---|
| `sdlc-delivery-orchestrator` | Orchestrate the complete lifecycle and route to the right skill. |
| `sdlc-idea-framing` | Clarify raw product ideas. |
| `sdlc-market-user-discovery` | Research users, market, and evidence. |
| `sdlc-prd-requirements` | Write precise, testable PRDs and requirements. |
| `sdlc-domain-modeling` | Model business concepts, rules, and invariants. |
| `sdlc-bounded-context-map` | Map DDD context boundaries and ownership. |
| `sdlc-bdd-specifications` | Specify behavior with examples and Gherkin. |
| `sdlc-ux-product-design` | Design user journeys, flows, and states. |
| `sdlc-ui-design-system` | Plan UI components, tokens, and accessibility. |
| `sdlc-architecture-rfc` | Create architecture RFCs and ADR candidates. |
| `sdlc-application-architecture` | Design modules, layers, services, and boundaries. |
| `sdlc-data-architecture` | Design data ownership, schemas, migrations, and audit. |
| `sdlc-security-privacy-compliance` | Integrate AppSec, privacy, compliance, and threat modeling. |
| `sdlc-ai-coding-governance` | Govern AI-assisted coding workflows. |
| `sdlc-ai-product-architecture` | Design LLM, RAG, agent, eval, safety, and AI observability. |
| `sdlc-delivery-roadmap-backlog` | Slice roadmap and backlog into executable work. |
| `sdlc-implementation-planning` | Plan safe code changes. |
| `sdlc-code-change-execution` | Execute scoped repository changes. |
| `sdlc-test-strategy` | Design quality strategy and tests by risk. |
| `sdlc-code-review` | Review code against quality gates. |
| `sdlc-ci-cd-platform` | Design delivery platform and CI/CD. |
| `sdlc-observability-reliability` | Design SLOs, telemetry, alerts, and runbooks. |
| `sdlc-incident-support-feedback` | Close incident, support, and feedback loops. |
| `sdlc-scalability-cost` | Balance performance, scale, and FinOps. |
| `sdlc-product-analytics` | Design metrics, tracking, experiments, and data quality. |
| `sdlc-documentation` | Keep documentation and onboarding useful. |
| `sdlc-third-party-ip-risk` | Review dependencies, licenses, vendors, and IP risk. |
| `sdlc-project-constitution` | Define non-negotiable engineering principles. |
| `sdlc-spec-clarification` | Resolve spec ambiguity before planning. |
| `sdlc-requirements-checklist` | Unit-test the requirements themselves. |
| `sdlc-task-breakdown` | Create dependency-ordered executable tasks. |
| `sdlc-cross-artifact-analysis` | Audit spec, plan, tasks for consistency. |
| `sdlc-spec-convergence` | Reconcile built code against the spec. |
| `sdlc-design-brainstorming` | Design gate before any implementation. |
| `sdlc-test-driven-development` | Red, green, refactor with proof. |
| `sdlc-systematic-debugging` | Root cause before any fix. |
| `sdlc-verification-before-completion` | Evidence before any done claim. |
| `sdlc-subagent-driven-execution` | Execute tasks with fresh agents and reviews. |
| `sdlc-branch-worktree-lifecycle` | Isolate work and finish branches safely. |
| `sdlc-receiving-code-review` | Evaluate review feedback before implementing. |
| `sdlc-legacy-inventory-registry` | Freeze everything the legacy system exposes. |
| `sdlc-legacy-reverse-engineering` | Extract business rules and behavior from legacy code. |
| `sdlc-characterization-testing` | Pin legacy behavior with oracles and golden masters. |
| `sdlc-migration-batch-orchestration` | Drive a migration in verified vertical batches. |
| `sdlc-independent-verification` | Refute porting claims in a separate context. |
| `sdlc-reachability-anti-simulation` | Block unrouted code and faked clients. |
| `sdlc-system-merge` | Merge two systems or estates into one target. |
| `sdlc-data-migration-reconciliation` | Move and reconcile data with proof. |
| `sdlc-cutover-rollback` | Rehearse go-live, parallel run, and retreat. |
| `sdlc-performance-budgets` | Set and enforce measurable performance budgets. |
| `sdlc-accessibility-engineering` | Build and verify WCAG-conformant interfaces. |
| `sdlc-api-versioning-deprecation` | Evolve APIs without breaking consumers. |

## Spec-Driven and Disciplined Execution

Inspired by GitHub Spec Kit and Superpowers (see `docs/references/method-sources.md`), the suite adds a spec-driven chain and execution discipline:

`constitution -> brainstorm -> clarify -> checklist -> plan -> tasks -> analyze + trace -> TDD execution (subagent-driven, worktree-isolated) -> verify against definition of done -> review -> converge -> retrospective`

- Spec chain: `sdlc-project-constitution`, `sdlc-design-brainstorming`, `sdlc-spec-clarification`, `sdlc-requirements-checklist`, `sdlc-task-breakdown`, `sdlc-cross-artifact-analysis`, `sdlc-spec-convergence`.
- Execution discipline: `sdlc-test-driven-development`, `sdlc-systematic-debugging`, `sdlc-verification-before-completion`, `sdlc-subagent-driven-execution`, `sdlc-branch-worktree-lifecycle`, `sdlc-receiving-code-review`.
- Beyond both sources: `sdlc-traceability-ledger` (script-checked requirement-to-test chain), `sdlc-definition-of-done` (depth-scaled, evidence-first), `sdlc-agent-context-engineering`, `sdlc-tasks-to-issues`, `sdlc-delivery-retrospective`, `sdlc-skill-evaluation`.
- Meta: `sdlc-skill-evaluation`.

Supporting assets: `docs/references/depth-matrix.md` (which steps at Lean, Standard, Enterprise-ready), `harnesses/spec-driven-delivery.yaml`, `pipelines/spec-driven-delivery.md`, `scripts/sdlc_trace.py` with `scripts/test_sdlc_trace.py`, and a worked fixture in `examples/spec-driven-trace/`.

```bash
python scripts/sdlc_trace.py --target examples/spec-driven-trace --strict
```

## Legacy Migration and System Merge

Migrating a legacy estate, or merging two, fails when progress is counted on what was written instead of what existed, and when the author of a change is its only judge. This layer fixes both:

`frozen registry -> batches -> reverse engineering -> oracles -> test-first build -> reachability ratchet -> independent verification and visa -> rehearsed cutover -> lessons`

- Skills: `sdlc-legacy-inventory-registry`, `sdlc-legacy-reverse-engineering`, `sdlc-characterization-testing`, `sdlc-migration-batch-orchestration`, `sdlc-independent-verification`, `sdlc-reachability-anti-simulation`, `sdlc-system-merge`, `sdlc-data-migration-reconciliation`, `sdlc-cutover-rollback`.
- Agents: `legacy-analyst` and `independent-verifier` (the verifier runs in a separate context and cannot visa its own work).
- Harnesses: `harnesses/legacy-migration.yaml`, `harnesses/system-merge.yaml`; pipelines `pipelines/legacy-migration.md`, `pipelines/system-merge.md`.
- Tool: `scripts/sdlc_registry.py` (init, check, report, sample, claim, visa, ratchet), tested by `scripts/test_sdlc_registry.py`.

```bash
python scripts/sdlc_registry.py report docs/migration/registry.csv
python examples/legacy-migration-invoicing/run_example.py   # full worked example
```

Specialized quality skills: `sdlc-performance-budgets`, `sdlc-accessibility-engineering`, `sdlc-api-versioning-deprecation`.

## Presets

- `fintech-regulated`
- `b2b-saas`
- `ai-agent-product`
- `mobile-offline`
- `marketplace`
- `data-product`
- `enterprise-ready`
- `legacy-migration`
- `system-merge`
- `healthtech-regulated`
- `public-sector`
- `ecommerce-retail`

Presets are stored in `presets/` and tune skill depth for domain-specific projects.

## Agent Factory

The automation layer separates method from runtime:

- `skills/`: reusable SDLC methods and guardrails.
- `agents/`: specialist role definitions, permissions, gates, and handoffs.
- `harnesses/`: executable state machines for idea-to-production, feature-to-production, spec-driven delivery, legacy migration, system merge, and production feedback.
- `pipelines/`: human-readable operating procedures for PRs, releases, and production learning.
- `integrations/`: adapters for Codex, Claude Code, Hermes, OpenClaw, GitHub Actions, and MCP.
- `data/agent-runtime-matrix.csv`: runtime and gate mapping by agent.

Primary agents:

| Agent | Role |
|---|---|
| `orchestrator` | Split work, select skills, enforce gates, and route handoffs. |
| `product-strategist` | Clarify idea, evidence, PRD, MVP, roadmap, and metrics. |
| `domain-architect` | Model domain rules, bounded contexts, and BDD examples. |
| `ux-ui-designer` | Define journeys, UI states, accessibility, and tracking. |
| `solution-architect` | Decide architecture, data, APIs, identity, and tradeoffs. |
| `fullstack-builder` | Implement approved vertical slices in isolated branches or worktrees. |
| `qa-test-engineer` | Build acceptance, regression, and risk-based test evidence. |
| `security-reviewer` | Review AppSec, privacy, tenants, dependencies, and AI risk. |
| `devops-sre` | Prepare CI/CD, reliability, observability, rollback, and runbooks. |
| `code-reviewer` | Make the merge-gate decision from diff, specs, tests, and risk. |
| `release-manager` | Own go/no-go, rollout, post-release checks, and production learning. |
| `legacy-analyst` | Inventory legacy sources, freeze the registry, extract rules, and classify convergence. |
| `independent-verifier` | Refute claimed work in a separate context and grant or refuse visas. |

## Automated Workflows

Idea to PR:

```text
Use harnesses/app-idea-to-production.yaml.
Start from this app idea, create the product docs, BDD, architecture, implementation plan, then implement the first vertical slice.
Stop before production deployment.
```

Feature to production:

```text
Use harnesses/feature-to-production.yaml.
Route this feature through behavior, impact, implementation, QA, security, review, and release readiness.
```

Spec-driven delivery:

```text
Use harnesses/spec-driven-delivery.yaml.
Take this feature through design, clarified spec, traceable tasks, test-first build, verification evidence, convergence, and retrospective.
```

Production feedback loop:

```text
Use harnesses/production-feedback-loop.yaml.
Turn this incident, support signal, analytics anomaly, or reliability issue into a fix, learning, or product decision.
```

Human approval remains required for product scope, durable architecture choices, dependency additions, secrets, customer data, payments, destructive migrations, and production deployment.

## Examples

- `examples/fintech-cfo-b2b/sdlc-case-study.md`: compact case study for a fintech CFO product.
- `examples/agent-factory-idea-to-pr/`: complete automation example showing how a raw app idea becomes a task graph, artifact map, simulated PR, and review gate across Codex, Claude Code, and Hermes prompts.
- `examples/hermes-releasepilot-signal-clustering/`: complete Hermes operating pack for a ReleasePilot Signal Clustering feature, including profile context, project skills, task graph, BDD, red tests, feature flag, simulated PR, review gate, production follow-up, and ROI loop.

## Scaffold Project Docs

From this repository:

```bash
python skills/sdlc-delivery-orchestrator/scripts/scaffold_sdlc_docs.py --target /path/to/project
```

This copies reusable templates from `templates/docs/` into the target project's `docs/` tree without overwriting existing files unless `--force` is passed.

## Sources

See:

- `docs/references/standards-map.md`
- `docs/references/market-skill-benchmark.md`
- `docs/references/sourcing-matrix.md`
- `docs/references/agent-runtime-matrix.md`

## Runtime Adapters

- `integrations/codex/README.md`
- `integrations/claude-code/README.md`
- `integrations/hermes/README.md`
- `integrations/openclaw/README.md`
- `integrations/github-actions/README.md`
- `integrations/mcp/README.md`

## License

MIT
