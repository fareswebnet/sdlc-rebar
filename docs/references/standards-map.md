# Standards Map - AI SDLC Skills

Date: 2026-08-01

Ce document cartographie les standards, frameworks et bonnes pratiques à utiliser pour peupler la suite `ai-sdlc-skills`. Il ne remplace pas les sources originales. Il sert de boussole pour créer des skills originaux, cohérents et publiables.

## Principes de sourcing

| Type de source | Usage dans la suite | Règle |
|---|---|---|
| Standard normatif | Définir les exigences, vocabulaires, contrôles et checklists | Citer, paraphraser, ne pas copier |
| Framework reconnu | Structurer la méthode et les livrables | Adapter au format skill et au mode Lean/Standard/Enterprise |
| Skill public existant | Benchmark, inspiration, éventuellement dépendance recommandée | Vérifier licence, provenance, install count, contenu, scripts et risques |
| Pratique marché | Compléter les standards trop abstraits | Transformer en procédure vérifiable |
| Création originale | Relier les sources en workflow repo-first | Préserver une interface `sdlc-*` stable |

## Références transverses

| Référence | Rôle | Skills concernés |
|---|---|---|
| ISO/IEC/IEEE 12207 - Software life cycle processes | Cadre complet de cycle de vie logiciel | Tous, surtout `sdlc-delivery-system`, `` |
| ISO/IEC/IEEE 29148 - Requirements engineering | Exigences, attributs de qualité des exigences, information items | `sdlc-prd-requirements`, `sdlc-bdd-specifications`, `sdlc-quality-test-strategy` |
| ISO/IEC/IEEE 42010 - Architecture description | Description d'architecture, viewpoints, concerns, stakeholders | `sdlc-architecture-rfc`, `sdlc-application-architecture` |
| ISO/IEC 25010:2023 - Product quality model | Modèle de qualité produit: sécurité, fiabilité, maintenabilité, performance, utilisabilité, etc. | `sdlc-quality-test-strategy`, `sdlc-code-review-quality-gate`, `` |
| DORA metrics | Mesure delivery: throughput, instability, amélioration continue | `sdlc-delivery-system`, `sdlc-devops-ci-cd-platform`, `sdlc-observability-reliability` |

Sources:

- ISO/IEC/IEEE 12207: https://standards.ieee.org/ieee/12207/11416/
- ISO/IEC/IEEE 29148: https://www.iso.org/standard/72089.html
- ISO/IEC/IEEE 42010: https://www.iso.org/standard/74393.html
- ISO/IEC 25010:2023: https://www.iso.org/standard/78176.html
- DORA metrics: https://dora.dev/guides/dora-metrics/

## Produit et discovery

| Référence | Ce qu'on reprend | Skills concernés |
|---|---|---|
| PRD agile Atlassian | PRD concis, collaboratif, vivant, orienté objectifs, hypothèses, user stories, design, questions ouvertes, hors périmètre | `sdlc-prd-requirements`, `sdlc-idea-framing` |
| Shape Up | Shaping, appetite, pitch, risques, no-gos, fixed time variable scope | `sdlc-idea-framing`, `sdlc-delivery-roadmap-backlog`, `sdlc-implementation-planning` |
| Dual-track discovery/delivery | Discovery continue séparée de l'exécution, mais connectée aux décisions | `sdlc-market-user-discovery`, `sdlc-delivery-system` |

Sources:

- Atlassian PRD: https://www.atlassian.com/agile/product-management/requirements/
- Shape Up pitch: https://basecamp.com/shapeup/1.5-chapter-06
- Shape Up shaping principles: https://basecamp.com/shapeup/1.1-chapter-02

## Domain modeling, bounded contexts et architecture

| Référence | Ce qu'on reprend | Skills concernés |
|---|---|---|
| Domain-Driven Design | Ubiquitous language, domain model, strategic design, complex domain logic | `sdlc-domain-modeling` |
| Bounded Context | Découpage du domaine, cohérence du modèle, relations entre contextes | `sdlc-bounded-context-map` |
| C4 model | Diagrams system context, containers, components, code; diagrams as communication and onboarding | `sdlc-architecture-rfc`, `sdlc-application-architecture`, `sdlc-documentation-knowledge` |
| ADR | Context, decision, consequences, alternatives, lifecycle des décisions | `sdlc-architecture-rfc`, `sdlc-delivery-retrospective` |
| Architecture styles | Modular monolith, hexagonal, clean, microservices, event-driven, CQRS, event sourcing, serverless | `sdlc-architecture-rfc`, `sdlc-application-architecture` |

Sources:

- DDD overview: https://martinfowler.com/bliki/DomainDrivenDesign.html
- Bounded Context: https://martinfowler.com/bliki/BoundedContext.html
- C4 model: https://c4model.com/
- AWS ADR guidance: https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html
- Google Cloud ADR overview: https://docs.cloud.google.com/architecture/architecture-decision-records

## BDD comportemental

| Référence | Ce qu'on reprend | Skills concernés |
|---|---|---|
| Cucumber BDD | Discovery, formulation, automation; BDD comme collaboration par exemples, pas seulement tests | `sdlc-bdd-specifications`, `sdlc-quality-test-strategy` |
| Gherkin | Given/When/Then lisible par humains et machines | `sdlc-bdd-specifications` |
| Example mapping | Rules, examples, questions, edge cases | `sdlc-bdd-specifications`, `sdlc-prd-requirements` |

Source:

- Cucumber BDD: https://cucumber.io/docs/bdd/

## UX, UI et accessibilité

| Référence | Ce qu'on reprend | Skills concernés |
|---|---|---|
| WCAG 2.2 | Accessibilité web, niveaux A/AA/AAA, exigences de conformité | `sdlc-ux-product-design`, `sdlc-ui-design-system`, `sdlc-quality-test-strategy` |
| Nielsen Norman Group | Journey mapping, usability, heuristiques UX | `sdlc-ux-product-design` |
| Design systems | Tokens, composants, états UI, responsive, conventions d'interaction | `sdlc-ui-design-system` |

Sources:

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- NN/g journey mapping: https://www.nngroup.com/articles/journey-mapping-101/

## API, events et intégrations

| Référence | Ce qu'on reprend | Skills concernés |
|---|---|---|
| OpenAPI | Contrats REST/HTTP machine-readable, schémas, endpoints, erreurs, sécurité | `sdlc-api-versioning-deprecation` |
| AsyncAPI | Contrats event-driven/message-driven, channels, messages, operations, bindings | `sdlc-api-versioning-deprecation`, `sdlc-application-architecture` |
| Contract testing | Backward compatibility, consumer/provider contracts | `sdlc-quality-test-strategy`, `sdlc-api-versioning-deprecation` |

Sources:

- OpenAPI Specification: https://spec.openapis.org/oas/latest.html
- AsyncAPI Specification: https://www.asyncapi.com/docs/reference/specification/latest

## Sécurité, privacy, compliance et supply chain

| Référence | Ce qu'on reprend | Skills concernés |
|---|---|---|
| NIST SSDF SP 800-218 | Secure software development practices intégrables dans tout SDLC | `sdlc-security-privacy-compliance`, `sdlc-code-review-quality-gate`, `sdlc-devops-ci-cd-platform` |
| OWASP SAMM | Maturité AppSec, roadmap d'amélioration, approche risk-driven | `sdlc-security-privacy-compliance`, `` |
| OWASP ASVS | Exigences de vérification sécurité applicative | `sdlc-security-privacy-compliance`, `sdlc-quality-test-strategy` |
| OWASP Cheat Sheets | Bonnes pratiques concrètes par risque | `sdlc-code-review-quality-gate`, `sdlc-security-privacy-compliance` |
| SLSA | Supply chain, provenance, niveaux de confiance build/source | `sdlc-third-party-ip-risk`, `sdlc-devops-ci-cd-platform` |
| OWASP Top 10 / LLM Top 10 | Risques web et risques spécifiques LLM/agents | `sdlc-security-privacy-compliance`, `sdlc-ai-product-architecture` |

Sources:

- NIST SSDF: https://csrc.nist.gov/pubs/sp/800/218/final
- OWASP SAMM: https://owasp.org/www-project-samm/
- OWASP ASVS: https://github.com/OWASP/ASVS
- OWASP Cheat Sheets: https://cheatsheetseries.owasp.org/
- SLSA: https://slsa.dev/spec/v1.2/
- OWASP LLM Top 10: https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/

## DevOps, release, observabilité et reliability

| Référence | Ce qu'on reprend | Skills concernés |
|---|---|---|
| DORA metrics | Change lead time, deployment frequency, failed deployment recovery time, change fail rate, deployment rework rate | `sdlc-devops-ci-cd-platform`, `sdlc-observability-reliability`, `` |
| OpenTelemetry | Traces, metrics, logs, instrumentation vendor-neutral | `sdlc-observability-reliability` |
| Google SRE | SLI, SLO, error budget, alerting utile, production best practices | `sdlc-observability-reliability`, `sdlc-definition-of-done` |
| Twelve-Factor App | Config, stateless processes, backing services, dev/prod parity | `sdlc-devops-ci-cd-platform`, `sdlc-application-architecture` |

Sources:

- DORA metrics: https://dora.dev/guides/dora-metrics/
- OpenTelemetry docs: https://opentelemetry.io/docs/
- Google SRE SLOs: https://sre.google/sre-book/service-level-objectives/
- Twelve-Factor App: https://12factor.net/

## Performance, scalabilité et coûts

| Référence | Ce qu'on reprend | Skills concernés |
|---|---|---|
| FinOps Framework | Business value drives technology decisions, ownership des coûts, data accessible, collaboration finance/tech/product | `sdlc-performance-scalability-cost` |
| SRE capacity/reliability practices | Latence, disponibilité, saturation, error budgets | `sdlc-observability-reliability`, `sdlc-performance-scalability-cost` |
| Cloud provider architecture centers | Patterns de résilience, coût, scalabilité, IaC, migration | `sdlc-architecture-rfc`, `sdlc-devops-ci-cd-platform` |

Source:

- FinOps Framework: https://www.finops.org/framework/

## IA, LLM et agents

| Référence | Ce qu'on reprend | Skills concernés |
|---|---|---|
| NIST AI RMF | Trustworthiness, risk management, governance, measurement | `sdlc-ai-product-architecture`, `sdlc-ai-assisted-development` |
| NIST Generative AI Profile | Risques spécifiques genAI, test/evaluation, gouvernance | `sdlc-ai-product-architecture` |
| OWASP LLM Top 10 | Prompt injection, data leakage, unsafe tool use, supply chain LLM | `sdlc-ai-product-architecture`, `sdlc-security-privacy-compliance` |
| Agent Skills open ecosystem | Format SKILL.md, progressive disclosure, distribution multi-agent | Tous les skills, surtout packaging |

Sources:

- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI RMF 1.0: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
- OWASP LLM Top 10: https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/
- OpenAI Skills catalog: https://github.com/openai/skills
- GitHub Copilot Agent Skills docs: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills
- skills.sh docs: https://www.skills.sh/docs

