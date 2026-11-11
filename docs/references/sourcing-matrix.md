# Sourcing Matrix - AI SDLC Skills v1

Date: 2026-08-01

Légende:

- **Fondation**: standards/frameworks à utiliser dans le skill.
- **Benchmark marché**: skills ou catalogues publics à auditer.
- **Décision**:
  - `Créer`: skill original nécessaire.
  - `Adapter`: créer un skill original mais reprendre des patterns existants.
  - `Recommander`: ne pas intégrer, mais mentionner comme skill externe utile.

## Matrice synthétique

| # | Skill cible | Fondation | Benchmark marché | Décision | Livrables attendus |
|---:|---|---|---|---|---|
| 1 | `sdlc-delivery-system` | ISO 12207, DORA, Shape Up, dual-track | `writing-plans`, `implement`, `handoff`, skills orchestration | Créer | plan de cycle, routing skills, mode Lean/Standard/Enterprise, traceability map |
| 3 | `sdlc-idea-framing` | Lean Startup, Shape Up, PRD agile | `brainstorming`, `grill-me`, `research` | Adapter | problème, audience, alternatives, hypothèses, no-gos |
| 4 | `sdlc-market-user-discovery` | Product discovery, interviews, opportunity mapping | `research`, AI research skills | Adapter | segments, jobs, interviews, preuves, incertitudes |
| 6 | `sdlc-prd-requirements` | ISO 29148, Atlassian PRD, agile requirements | `to-prd`, `to-spec`, `to-tickets` | Adapter | PRD, requirements testables, out-of-scope, assumptions |
| 7 | `sdlc-domain-modeling` | DDD, ubiquitous language, domain rules | `domain-modeling`, `ubiquitous-language` | Adapter | vocabulaire, entités, value objects, invariants, règles métier |
| 8 | `sdlc-bounded-context-map` | DDD strategic design, bounded context, context mapping | `domain-modeling`, architecture skills | Créer | context map, ownership, upstream/downstream, anticorruption layer |
| 9 | `sdlc-bdd-specifications` | Cucumber BDD, Gherkin, example mapping, ISO 29148 | `tdd`, `test-driven-development`, `to-spec` | Adapter | scenarios Given/When/Then, examples, rules, open questions, living docs |
| 10 | `sdlc-ux-product-design` | WCAG, journey mapping, usability heuristics | `frontend-design`, `design-an-interface`, `ui-ux-pro-max` | Adapter | user journeys, flows, states, edge cases UX |
| 11 | `sdlc-ui-design-system` | WCAG, design systems, component conventions | `web-design-guidelines`, `shadcn`, `vercel-react-best-practices` | Adapter | tokens, components, responsive rules, accessibility states |
| 12 | `sdlc-architecture-rfc` | ISO 42010, C4, ADR, architecture trade-offs | `improve-codebase-architecture`, `codebase-design` | Adapter | RFC, C4 diagrams, ADR candidates, trade-off table |
| 13 | `sdlc-application-architecture` | Hexagonal, clean, modular monolith, microservices, CQRS, event-driven | architecture/codebase skills | Créer | module boundaries, dependency rules, services, ports/adapters |
| 14 | `sdlc-data-database-architecture` | Data ownership, PostgreSQL patterns, migration safety, audit, multi-tenant data | `supabase-postgres-best-practices`, data platform skills | Adapter | data model, schemas, indexes, migrations, retention, analytics needs |
| 17 | `sdlc-security-privacy-compliance` | NIST SSDF, OWASP SAMM, ASVS, Top 10, GDPR questions | `checking-owasp-compliance`, `stride-analysis-patterns`, SAST skills | Adapter | threat model, security requirements, privacy review, compliance release gate |
| 18 | `sdlc-ai-assisted-development` | Agent Skills spec, AI coding guardrails, traceability, review loops | OpenAI Skills, GitHub Copilot Skills, `skill-creator`, `writing-great-skills` | Créer | context pack, task decomposition, agent roles, output evaluator |
| 19 | `sdlc-ai-product-architecture` | NIST AI RMF, OWASP LLM Top 10, eval harness practices, RAG patterns | NVIDIA AI/RAG skills, LLM security skills | Adapter | AI requirements, prompt/context design, RAG architecture, eval dataset, safety controls |
| 20 | `sdlc-delivery-roadmap-backlog` | Shape Up, agile backlog, prioritization, DORA flow | `to-tickets`, `to-issues`, planning skills | Adapter | roadmap now/next/later, backlog slices, dependencies, ticket readiness |
| 21 | `sdlc-implementation-planning` | Vertical slicing, risk-first delivery, architecture conformance | `implement`, `writing-plans`, `handoff` | Adapter | implementation plan, files impacted, validation plan, rollback notes |
| 22 | `sdlc-code-change-execution` | Repo-first engineering, TDD, code review discipline | `implement`, `diagnosing-bugs`, `systematic-debugging` | Adapter | scoped code changes, tests, migration scripts, verification notes |
| 23 | `sdlc-quality-test-strategy` | ISO 25010, ISO 29148, BDD, test pyramid, contract/e2e/regression | `tdd`, `qa`, `lint-and-validate`, `tdd-workflow` | Adapter | test strategy, acceptance tests, coverage by risk, regression plan |
| 24 | `sdlc-code-review-quality-gate` | ISO 25010, secure coding, maintainability, review checklists | code review skills, `requesting-code-review` | Adapter | review checklist, findings, merge gate, residual risk |
| 25 | `sdlc-devops-ci-cd-platform` | DORA, NIST SSDF, SLSA, Twelve-Factor, CI/CD patterns | `deployment-pipeline-design`, Azure/cloud skills | Adapter | pipeline design, env strategy, artifact/provenance, developer setup |
| 27 | `sdlc-observability-reliability` | OpenTelemetry, Google SRE, SLO/error budgets, DORA | Agent Skill Exchange SRE, `azure-reliability`, observability skills | Adapter | SLIs/SLOs, dashboards, alerts, traces/logs/metrics, runbooks |
| 28 | `sdlc-incident-support-feedback` | SRE incident response, postmortems, support triage | support/success collections, incident ops skills | Adapter | incident timeline, postmortem, support signal triage, feedback-to-roadmap |
| 29 | `sdlc-performance-scalability-cost` | ISO 25010 performance, SRE, FinOps, cloud cost models | `azure-cost`, `azure-cost-optimization`, performance skills | Adapter | bottleneck review, capacity model, unit cost model, cost guardrails |
| 30 | `sdlc-product-analytics-experimentation` | Product analytics, experimentation, data quality, metric governance | analytics/growth collections, feature flag skills | Créer | tracking plan, KPI definitions, experiments, dashboard readiness |
| 32 | `sdlc-documentation-knowledge` | ISO 12207 documentation, C4, ADR, OpenAPI docs, runbooks | docs/devrel skills, `edit-article`, API docs skills | Adapter | docs architecture, onboarding, API docs, runbooks, freshness checks |
| 33 | `sdlc-third-party-ip-risk` | SLSA, OpenSSF practices, SBOM, license review, vendor risk | supply-chain/security skills, dependency review skills | Créer | dependency register, license/IP review, vendor lock-in, AI-generated code policy |

## Presets optionnels

| Preset | Sources principales | Rôle |
|---|---|---|
| `preset-fintech-regulated` | NIST SSDF, OWASP ASVS, auditability, privacy, data retention, payment/KYC patterns | Renforce sécurité, audit, données sensibles, conformité, traçabilité |
| `preset-b2b-saas` | Multi-tenancy, billing, entitlement, admin/back-office, support feedback | Oriente architecture produit B2B |
| `preset-ai-agent-product` | NIST AI RMF, OWASP LLM Top 10, RAG, eval, tool safety | Active le bloc AI product/LLM/agent |
| `preset-mobile-offline` | Mobile architecture, offline sync, app store release, device capabilities | Active workflows mobile/PWA/offline |
| `preset-marketplace` | Payments, trust/safety, dispute flows, multi-sided analytics | Ajoute workflows multi-acteurs |
| `preset-data-product` | Data quality, BI, pipelines, warehouse, dbt/Airflow patterns | Renforce data architecture/analytics |
| `preset-enterprise-ready` | ISO/IEC/IEEE, OWASP SAMM, SLSA, auditability, governance | Ajoute exigences de due diligence et gouvernance |

## Gaps marché à combler

1. Orchestration complète SDLC, pas seulement des skills isolés.
2. Passage explicite du domaine métier vers BDD, puis architecture, puis tests.
3. Bounded contexts comme artefact vivant, relié au code et aux données.
4. Gestion des données et SGBD reliée au produit, aux permissions et au multi-tenant.
5. AI-assisted development avec garde-fous et traçabilité spec-to-code.
6. AI product architecture avec evaluation harness, RAG, prompt/context, safety et observability.
7. Production loop complète: SLO, incident, support feedback, product analytics, DORA.
8. Coûts/FinOps traités comme contrainte d'architecture.
9. Documentation repo-first, versionnée, audit-ready.
10. Matrice de provenance par skill pour crédibilité open source et due diligence.

## Prochaine étape recommandée

Créer le squelette du dépôt `ai-sdlc-skills` avec:

```text
README.md
LICENSE
docs/references/standards-map.md
docs/references/market-skill-benchmark.md
docs/references/sourcing-matrix.md
skills/sdlc-*/
presets/
examples/
templates/docs/
```

Puis générer les 33 `SKILL.md` en appliquant cette matrice comme source de vérité.

