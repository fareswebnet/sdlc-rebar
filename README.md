# AI SDLC Skills

An agent skill suite for the full product-tech software delivery lifecycle.

This repository packages 33 `$sdlc-*` skills and optional presets to help a team move from idea to production learning:

`idea -> discovery -> PRD -> domain model -> bounded contexts -> BDD -> UX/UI -> architecture/data -> contracts -> backlog -> implementation -> tests -> release -> observability -> incidents/support -> improvement`

The suite is designed for startups and scale-ups by default, but each skill can be used in Lean, Standard, or Enterprise-ready depth.

## What This Is

- A repo-first SDLC operating system for AI-assisted product and engineering work.
- A set of portable agent skills using `SKILL.md` folders.
- A standards-informed implementation layer over ISO/IEC/IEEE, DDD, BDD, OWASP, NIST, SLSA, DORA, OpenTelemetry, SRE, FinOps, WCAG, OpenAPI, AsyncAPI, and AI risk practices.

## What This Is Not

- Not legal, accounting, financial, compliance, investment, or security certification advice.
- Not a replacement for qualified review in regulated or high-risk contexts.
- Not a command to over-document every project. Use the depth that fits the risk.

## Install

Copy or install the `skills/` folders into a compatible agent skills location, or reference this repository from tooling that supports Agent Skills.

For Codex-style local use:

```bash
cp -R skills/sdlc-* ~/.codex/skills/
```

Restart the agent session so new skills are discovered.

## Skills

| Skill | Purpose |
|---|---|
| `$sdlc-delivery-system` | Orchestrate the complete lifecycle and route to the right skill. |
| `$sdlc-maturity-assessment` | Score maturity, gaps, and improvement roadmap. |
| `$sdlc-idea-framing` | Clarify raw product ideas. |
| `$sdlc-market-user-discovery` | Research users, market, and evidence. |
| `$sdlc-product-strategy` | Shape outcomes, MVP, appetite, and roadmap. |
| `$sdlc-prd-requirements` | Write precise, testable PRDs and requirements. |
| `$sdlc-domain-modeling` | Model business concepts, rules, and invariants. |
| `$sdlc-bounded-context-map` | Map DDD context boundaries and ownership. |
| `$sdlc-bdd-specifications` | Specify behavior with examples and Gherkin. |
| `$sdlc-ux-product-design` | Design user journeys, flows, and states. |
| `$sdlc-ui-design-system` | Plan UI components, tokens, and accessibility. |
| `$sdlc-architecture-rfc` | Create architecture RFCs and ADR candidates. |
| `$sdlc-application-architecture` | Design modules, layers, services, and boundaries. |
| `$sdlc-data-database-architecture` | Design data ownership, schemas, migrations, and audit. |
| `$sdlc-api-integration-contracts` | Specify APIs, events, webhooks, and contracts. |
| `$sdlc-identity-access-multitenancy` | Model auth, permissions, tenants, and privileged access. |
| `$sdlc-security-privacy-compliance` | Integrate AppSec, privacy, compliance, and threat modeling. |
| `$sdlc-ai-assisted-development` | Govern AI-assisted coding workflows. |
| `$sdlc-ai-product-architecture` | Design LLM, RAG, agent, eval, safety, and AI observability. |
| `$sdlc-delivery-roadmap-backlog` | Slice roadmap and backlog into executable work. |
| `$sdlc-implementation-planning` | Plan safe code changes. |
| `$sdlc-code-change-execution` | Execute scoped repository changes. |
| `$sdlc-quality-test-strategy` | Design quality strategy and tests by risk. |
| `$sdlc-code-review-quality-gate` | Review code against quality gates. |
| `$sdlc-devops-ci-cd-platform` | Design delivery platform and CI/CD. |
| `$sdlc-release-production-readiness` | Prepare safe releases and production readiness. |
| `$sdlc-observability-reliability` | Design SLOs, telemetry, alerts, and runbooks. |
| `$sdlc-incident-support-feedback` | Close incident, support, and feedback loops. |
| `$sdlc-performance-scalability-cost` | Balance performance, scale, and FinOps. |
| `$sdlc-product-analytics-experimentation` | Design metrics, tracking, experiments, and data quality. |
| `$sdlc-technical-debt-evolution` | Manage debt, refactoring, and architecture evolution. |
| `$sdlc-documentation-knowledge` | Keep documentation and onboarding useful. |
| `$sdlc-third-party-ip-risk` | Review dependencies, licenses, vendors, and IP risk. |

## Presets

- `$preset-fintech-regulated`
- `$preset-b2b-saas`
- `$preset-ai-agent-product`
- `$preset-mobile-offline`
- `$preset-marketplace`
- `$preset-data-product`
- `$preset-enterprise-ready`

Presets are stored in `presets/` and tune skill depth for domain-specific projects.

## Scaffold Project Docs

From this repository:

```bash
python skills/sdlc-delivery-system/scripts/scaffold_sdlc_docs.py --target /path/to/project
```

This copies reusable templates from `templates/docs/` into the target project's `docs/` tree without overwriting existing files unless `--force` is passed.

## Sources

See:

- `docs/references/standards-map.md`
- `docs/references/market-skill-benchmark.md`
- `docs/references/sourcing-matrix.md`

## License

MIT
