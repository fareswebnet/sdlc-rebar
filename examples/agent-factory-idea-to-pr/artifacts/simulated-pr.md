# Simulated PR - ReleasePilot First Vertical Slice

## Summary

Adds the first ReleasePilot vertical slice:

- release candidate intake model
- readiness gate classification
- risk summary view
- PR validation export
- tests for blocked and ready release states

## Product Behavior

The release owner can enter a feature brief, acceptance criteria, CI status, rollback note, and post-release checks. The app classifies the release candidate as:

- `blocked` when required evidence is missing
- `ready_for_review` when all review gates are present

The app can export a PR-ready validation summary listing behavior, checks, and residual risk.

## Architecture Impact

- Adds a `Readiness Evaluation` domain module.
- Keeps checklist rules as pure functions.
- Keeps external CI integration out of scope.
- Keeps production deployment out of scope.

## Data Impact

Introduces tenant-scoped records:

- `release_candidates`
- `readiness_gates`
- `validation_exports`

No destructive migration is required in this simulated first slice.

## Tests

Expected validation commands:

```bash
npm run lint
npm run typecheck
npm run test
```

Expected test coverage:

- blocks release when rollback note is missing
- marks release ready when all gates are present
- renders blocked and ready dashboard states
- prevents cross-tenant release candidate access

## Security And Privacy

- Tenant isolation is mandatory.
- Release metadata may contain confidential feature, customer, or incident details.
- Validation exports must not include secrets or raw environment variables.
- External CI, GitHub, Slack, or observability connectors require separate approval.

## Rollback

If the first slice causes issues:

- disable the release dashboard route
- keep data tables intact
- revert UI and domain module changes through the PR revert path

## Residual Risk

- Manual import can become tedious if teams need direct GitHub or CI integration.
- Gate classification is deterministic and may need organization-specific configuration later.
- No production deployment is included in this PR.

## Human Gate

Ready for human review. Not ready for production deployment until release-owner approval is recorded.
