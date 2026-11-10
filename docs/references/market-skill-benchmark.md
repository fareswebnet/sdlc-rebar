# Market Skill Benchmark - AI SDLC Skills

Date: 2026-08-01

Objectif: identifier ce qui existe déjà dans l'écosystème public des agent skills et décider ce qu'il faut réutiliser, adapter ou créer.

## Synthèse

Le marché des agent skills est actif, mais fragmenté. Les meilleurs catalogues fournissent beaucoup de skills spécialisés: frontend, code review, TDD, cloud, Azure, Supabase, sécurité, browser automation, documentation, image/document processing, product planning ponctuel. En revanche, je n'ai pas identifié de suite publique qui couvre de façon cohérente tout le cycle produit-tech complet avec:

- orchestrateur SDLC;
- mode Lean/Standard/Enterprise;
- artefacts versionnés dans le repo;
- traçabilité PRD -> BDD -> architecture -> tickets -> tests -> commits -> production;
- bounded contexts et domain modeling reliés aux specs BDD;
- coûts/FinOps, observabilité, incidents, support feedback et due diligence dans le même système.

Décision: créer une suite originale, mais benchmarker les meilleurs patterns de skills existants pour éviter de réinventer inutilement.

## Catalogues à surveiller

| Catalogue | Signal | Ce qu'il apporte | Limite pour notre suite |
|---|---|---|---|
| skills.sh | Leaderboard public, install counts, découverte via `npx skills` | Mesure d'adoption, noms de skills populaires, catégories pratiques | Popularité != qualité; revue manuelle obligatoire |
| OpenAI Skills | Catalog officiel Codex, format de référence | Structure de repo, packaging SKILL.md, curated/system skills | Ne fournit pas une suite SDLC complète prête à l'emploi |
| GitHub Copilot Agent Skills | Docs d'usage multi-emplacements, SKILL.md + ressources | Compatibilité écosystème, conventions pour agents dev | Plutôt documentation runtime que contenu SDLC |
| NVIDIA Verified Skills | Gouvernance, provenance, signatures, skill cards, security scanning | Bon modèle de trust, publication, ownership, limitations | Très orienté NVIDIA/AI infra, pas SDLC général |
| Agent Skill Exchange | Grand catalogue multi-agent, industry collections | Large veille, collections SRE/security/data/support | Qualité variable; chaque skill doit être audité |
| awesome-agent-skills | Liste communautaire par catégories | Découverte rapide par domaine: frontend, backend, testing, DevOps, security | Agrégateur, pas source de vérité |

Sources:

- skills.sh: https://www.skills.sh/
- skills.sh docs: https://www.skills.sh/docs
- OpenAI Skills: https://github.com/openai/skills
- GitHub Copilot Agent Skills: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills
- NVIDIA Verified Skills: https://docs.nvidia.com/skills
- Agent Skill Exchange: https://github.com/agentskillexchange/skills
- awesome-agent-skills: https://github.com/kodustech/awesome-agent-skills

## Skills publics repérés comme inspiration

| Domaine | Skills/catégories observés | Usage recommandé |
|---|---|---|
| Discovery / product | `grill-me`, `grilling`, `to-prd`, `to-spec`, `to-tickets`, `brainstorming`, `writing-plans` | Inspiration pour questionnement, transformation idée -> spec -> tickets |
| Domain / architecture | `domain-modeling`, `ubiquitous-language`, `improve-codebase-architecture`, `codebase-design`, `request-refactor-plan` | Benchmark de workflow architecture, mais besoin de cadrage DDD plus complet |
| Frontend / UI | `frontend-design`, `web-design-guidelines`, `design-an-interface`, `ui-ux-pro-max`, `shadcn`, `vercel-react-best-practices` | Inspiration forte pour `sdlc-ux-product-design` et `sdlc-ui-design-system` |
| Testing / qualité | `tdd`, `test-driven-development`, `qa`, `lint-and-validate`, `tdd-workflow` | Réutiliser patterns de workflow, mais élargir vers stratégie qualité complète |
| Security | `checking-owasp-compliance`, `stride-analysis-patterns`, `sast-configuration`, `auditing-access-control`, `pentest-checklist` | À auditer; nos skills doivent s'appuyer sur NIST SSDF, OWASP SAMM/ASVS |
| DevOps / cloud | `deployment-pipeline-design`, `azure-*`, `supabase`, `supabase-postgres-best-practices` | Inspirer presets stack/cloud, pas coeur agnostique |
| Observability / reliability | Agent Skill Exchange collections SRE & Incident Ops, `azure-reliability`, `clerk-observability` | Couverture dispersée; créer skill intégré reliability |
| Cost / FinOps | `azure-cost`, `azure-cost-optimization` | Bon signal pour cloud-specific presets; coeur doit rester FinOps agnostique |
| AI / RAG / agents | NVIDIA AIQ/RAG/sandbox skills, LLM/security skills | Inspirations pour AI product architecture, eval, guardrails |

## Critères de sélection avant réutilisation

Un skill public peut être repris comme dépendance recommandée ou modèle seulement si:

1. Licence claire et compatible avec un dépôt public MIT.
2. Source identifiable et réputée, ou audit manuel satisfaisant.
3. Frontmatter clair: `name` et `description` déclenchent le skill sans ambiguïté.
4. Scope précis, pas de comportement trop large ou destructif.
5. Scripts lisibles, sans réseau ou écriture implicite non documentée.
6. Pas de prompt injection cachée, instruction hostile ou exfiltration.
7. Installation suffisamment utilisée ou source suffisamment reconnue.
8. Valeur mesurable par rapport à une exécution sans skill.

## Décision de marché

| Question | Décision |
|---|---|
| Existe-t-il une suite SDLC publique exhaustive prête à installer ? | Non identifiée dans le benchmark public. |
| Faut-il copier des skills existants ? | Non. |
| Faut-il citer et benchmarker les catalogues ? | Oui. |
| Faut-il reprendre des patterns de skills populaires ? | Oui, après audit. |
| Faut-il créer notre propre interface `sdlc-*` ? | Oui, pour stabilité et cohérence. |
| Faut-il maintenir une matrice de provenance par skill ? | Oui, indispensable pour crédibilité et due diligence. |

