# Implementation Plan

## Slice Boundary

Implement only the first Signal Clustering vertical slice:

- manual signal batch input
- candidate cluster generation
- evidence and conflict display
- human validation decision
- spec draft generation after acceptance
- feature flag protection
- tenant isolation checks

Do not add external connectors, background jobs, model fine-tuning, customer notifications, or production deployment.

## Sequence

1. Add domain types for `Signal`, `CandidateCluster`, `ClusterEvidence`, `ClusterConflict`, and `ValidationDecision`.
2. Add pure clustering service behind `clusterSignals(signals, options)`.
3. Add validation guard so spec drafts require accepted clusters.
4. Add repository access with tenant-scoped queries.
5. Add review UI states for empty, loading, low-confidence, accepted, rejected, and error.
6. Add feature flag check around routes and actions.
7. Add audit event for denied cross-tenant access and validation decisions.
8. Update PR documentation and release notes draft.

## Suggested File Map

| Path | Purpose |
|---|---|
| `src/domain/signal-clustering/types.ts` | Domain types and enums. |
| `src/domain/signal-clustering/clusterSignals.ts` | Pure clustering decision function. |
| `src/domain/signal-clustering/generateSpecDraft.ts` | Spec draft guard and generator. |
| `src/app/signal-clustering/SignalClusterReview.tsx` | Review UI and action states. |
| `src/app/signal-clustering/routes.ts` | Feature-flagged route/action boundary. |
| `tests/domain/signal-clustering.test.ts` | Domain red-to-green tests. |
| `tests/components/signal-cluster-review.test.tsx` | UI state tests. |
| `docs/delivery/feature-flags.md` | Flag owner, rollout, rollback. |

## Agent Split

| Agent | Scope |
|---|---|
| Hermes orchestrator | Own task graph, gates, checkpoints, handoffs, and memory hygiene. |
| Product strategist | Product intent, assumptions, non-goals, and metrics. |
| Domain architect | Domain rules, bounded contexts, BDD scenarios. |
| Solution architect | ADR, data ownership, tenant isolation, feature flag, interface boundaries. |
| QA test engineer | Red tests and acceptance evidence. |
| Fullstack builder | Scoped implementation only after red gate. |
| Security reviewer | Tenant isolation, sensitive data, dependencies, prompt-injection risk. |
| Code reviewer | Merge decision from diff, tests, docs, and risk. |
| Release manager | Rollout plan, observability, post-release learning, ROI. |

## Stop Conditions

Stop and ask for a human decision when:

- BDD scenarios conflict with product intent
- implementation needs a new dependency
- implementation needs a migration
- existing auth or tenant isolation is unclear
- generated tests cannot run
- feature scope expands beyond Signal Clustering
- CI fails for unrelated reasons
- production rollout is requested
