# ReleasePilot SDLC Artifact Map

This is a compact example of the artifacts the agent system should produce or update before opening the first PR.

## Product

| File | Content |
|---|---|
| `docs/product/problem-statement.md` | Small teams ship without a shared view of release readiness and rollback risk. |
| `docs/product/prd.md` | First slice: generate checklist, classify missing gates, display risk summary, export PR validation text. |
| `docs/product/requirements-traceability.md` | Requirements mapped to BDD scenarios, tests, and PR sections. |

## Behavior

```gherkin
Feature: Release readiness checklist

Scenario: Feature is missing required validation gates
  Given a feature brief has acceptance criteria
  And the CI status is passing
  And no rollback note is present
  When the release owner opens the readiness view
  Then the system marks the release as blocked
  And shows "Rollback note missing" as a required gate
  And includes the missing gate in the PR validation export

Scenario: Feature is ready for review
  Given a feature brief has acceptance criteria
  And CI, tests, rollback notes, and post-release checks are present
  When the release owner opens the readiness view
  Then the system marks the release as ready for review
  And exports a PR summary with validation evidence
```

## Domain Model

| Concept | Meaning |
|---|---|
| Release Candidate | A feature or PR being evaluated before merge or deployment. |
| Readiness Gate | Required evidence such as tests, rollback, security review, or observability. |
| Risk Signal | Missing or weak evidence that may block merge or release. |
| Validation Export | PR-ready summary of behavior, checks, and residual risk. |

## Bounded Contexts

| Context | Responsibility |
|---|---|
| Feature Intake | Store brief, acceptance criteria, owner, and target release. |
| Readiness Evaluation | Evaluate gates and classify release status. |
| Validation Export | Generate PR body and release notes snippets. |
| Tenant Administration | Manage team, members, permissions, and audit trail. |

## Architecture

Recommended first-slice architecture:

- modular monolith
- server-rendered dashboard or small SPA
- relational database with tenant-scoped records
- checklist rules as pure domain functions
- no background workers for the first slice
- no external CI integration until the manual import flow proves useful

## Test Strategy

| Test | Coverage |
|---|---|
| Domain unit tests | Gate classification, blocked/ready states, missing rollback note. |
| Component tests | Empty, blocked, ready, and error states. |
| Acceptance tests | BDD scenarios for blocked and ready release candidates. |
| Security tests | Tenant-scoped access to release candidates. |

## Release Readiness

The first PR should not deploy to production. It should include:

- validation commands
- screenshots or local preview notes
- rollback notes
- dependency review
- post-release metrics to add later
