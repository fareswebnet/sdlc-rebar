# Depth Matrix

Which steps of the spec-driven chain are required at each depth. Skipping a step is allowed only with a stated reason in the decision log.

| Step | Skill | Lean | Standard | Enterprise-ready |
|---|---|---|---|---|
| Principles | `$sdlc-project-constitution` | once per repo, 5 rules max | versioned, with checks | versioned, owners, audit trail |
| Design gate | `$sdlc-design-brainstorming` | short written design | design doc with alternatives | design review with sign-off |
| Clarify | `$sdlc-spec-clarification` | one round | up to 5 questions per area | logged with owner and date |
| Requirement quality | `$sdlc-requirements-checklist` | self-check | peer review per domain | release-gate checklist |
| Plan | `$sdlc-implementation-planning` | bullet plan | plan with rollback | plan with risk register |
| Tasks | `$sdlc-task-breakdown` | task list | story-grouped, parallel-marked | plus issue sync |
| Consistency | `$sdlc-cross-artifact-analysis` | optional | required before code | required, report archived |
| Traceability | `$sdlc-traceability-ledger` | ids in tasks | script must pass | script `--strict` plus downstream links |
| Execution | `$sdlc-test-driven-development` | tests for risky paths | red-green-refactor | plus mutation or property tests where valuable |
| Isolation | `$sdlc-branch-worktree-lifecycle` | branch | worktree | worktree plus protected merge |
| Delegation | `$sdlc-subagent-driven-execution` | optional | two-stage review | plus independent security review |
| Done | `$sdlc-definition-of-done` | 5-10 lines | evidence per line | waivers need named owner |
| Convergence | `$sdlc-spec-convergence` | after build | after build and review | after build, review, and release |
| Learning | `$sdlc-delivery-retrospective` | after incidents | each release | each release with metrics |

## Risk escalators

Move up one depth when the change touches: payments, authentication or authorization, tenant isolation, personal data, irreversible migrations, regulated flows, or AI behavior visible to customers.
