# Pipeline: PR To Production

Use this pipeline after a change has passed product, implementation, test, security, and code-review gates.

## Outcome

Produce a controlled release with:

- green CI or documented residual failures
- rollout plan
- rollback plan
- migration plan when applicable
- observability and alert coverage
- runbook updates
- post-release checks

## Sequence

1. Run `release-manager` to create the release plan and go/no-go checklist.
2. Run `devops-sre` to verify CI/CD, environment, telemetry, SLOs, rollback, and incident readiness.
3. Run `security-reviewer` again if the release includes auth, secrets, payments, personal data, tenant isolation, infrastructure, or dependency changes.
4. Run `qa-test-engineer` for final smoke, acceptance, or regression evidence.
5. Record the human go/no-go decision.
6. Deploy through the normal release system.
7. Run post-release checks and capture production metrics.

## Gates

- Production deployment requires explicit human approval.
- Destructive migrations require backup, rehearsal, rollback, and owner sign-off.
- Critical flows must have telemetry and alert owners before release.
- Customer-impacting changes need support and rollback notes.

## Runtime Hints

- Codex: use hooks or CI jobs for deterministic checks, and keep deployment commands approval-gated.
- Claude Code: use permission modes to block risky commands until a human approves them.
- Hermes: use cron or project tasks for post-release monitoring and follow-up checks.
- GitHub Actions: use this pipeline as the review checklist behind protected branches.
