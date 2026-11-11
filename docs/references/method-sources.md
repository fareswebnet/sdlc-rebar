# Method Sources

Skills added in the speckit and superpowers enrichment adapt ideas into original wording; no text is copied.

| Skill | Inspiration | Idea adapted |
|---|---|---|
| `sdlc-project-constitution` | GitHub Spec Kit `constitution` | Versioned principles, sync-impact sweep, scope guard |
| `sdlc-spec-clarification` | Spec Kit `clarify` | Bounded one-at-a-time interview with recommended answers |
| `sdlc-requirements-checklist` | Spec Kit `checklist` | Checklists that test requirement quality |
| `sdlc-task-breakdown` | Spec Kit `tasks`, Superpowers `writing-plans` | Story-grouped, parallel-marked, exact-path tasks |
| `sdlc-cross-artifact-analysis` | Spec Kit `analyze` | Read-only severity-ranked consistency audit |
| `sdlc-spec-convergence` | Spec Kit `converge` | Assess code vs spec and append remaining tasks |
| `sdlc-design-brainstorming` | Superpowers `brainstorming` | Hard design gate before implementation |
| `sdlc-test-driven-development` | Superpowers `test-driven-development` | Verified red, minimal green, refactor |
| `sdlc-systematic-debugging` | Superpowers `systematic-debugging` | Root cause first, three-strikes rule |
| `sdlc-verification-before-completion` | Superpowers `verification-before-completion` | Evidence before claims |
| `sdlc-subagent-driven-execution` | Superpowers `subagent-driven-development`, `dispatching-parallel-agents` | Fresh agent per task, two-stage review |
| `sdlc-branch-worktree-lifecycle` | Superpowers `using-git-worktrees`, `finishing-a-development-branch` | Isolation and explicit finish options |
| `sdlc-code-review-reception` | Superpowers `receiving-code-review` | Verify feedback before implementing |

## Beyond the sources

These skills have no direct upstream equivalent and extend the idea of both projects.

| Skill | What it adds |
|---|---|
| `sdlc-traceability-ledger` | Id-based chain checked by `scripts/sdlc_trace.py`, extended to release and metrics |
| `sdlc-definition-of-done` | Depth- and risk-scaled criteria, each with a named evidence type and waiver rules |
| `sdlc-agent-context-engineering` | Designed context packs, subagent briefs, handoff notes, and honest memory |
| `sdlc-tasks-to-issues` | Approval-gated tracker sync with dependency links and reconciliation |
| `sdlc-delivery-retrospective` | Evidence-based loop that changes constitution, templates, skills, and CI |
| `sdlc-skill-evaluation` | Rubric-scored baseline-versus-skill evaluation with version history |

## Migration and specialized skills

The migration layer generalizes, in English and project-agnostic form, the practice of a real multi-source migration program (frozen registry as denominator, vertical batches, independent verifier, reachability ratchet, cumulative non-regression, separate visas per source). Project-specific paths, tools, and business rules were removed; commands here use `scripts/sdlc_registry.py`.

| Skill | Basis |
|---|---|
| `sdlc-legacy-inventory-registry`, `sdlc-migration-batch-orchestration` | Registry-driven migration programs |
| `sdlc-legacy-reverse-engineering`, `sdlc-characterization-testing` | Spec mining, golden master, differential testing |
| `sdlc-independent-verification`, `sdlc-reachability-anti-simulation` | Independent audit, mutation testing, ratchet gates |
| `sdlc-system-merge-convergence`, `sdlc-data-migration-reconciliation`, `sdlc-cutover-rollback` | Multi-source convergence, data reconciliation, strangler and parallel run |
| `sdlc-performance-budgets` | Web performance budgets, SRE objectives |
| `sdlc-accessibility-engineering` | WCAG 2.2 |
| `sdlc-api-versioning-deprecation` | Semantic versioning, consumer-driven contracts |

Both upstream projects are MIT-licensed; review their current licenses before copying any text.
