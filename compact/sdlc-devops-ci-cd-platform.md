# sdlc-devops-ci-cd-platform (compact)

When: Design developer environment, CI/CD, build, test, lint, typecheck, security scan, artifact provenance, environments, secrets, infrastructure as code, preview deployments, and developer experience.

Goal: Make build, test, preview, and deploy boring enough for fast teams.

Steps:
1. Inventory local setup, dependencies, scripts, env vars, services, and onboarding friction.
2. Design pipeline stages for build, lint, typecheck, tests, security, artifacts, and deploy.
3. Define environment strategy: local, preview, staging, production, data, secrets, and isolation.
4. Add supply-chain controls appropriate to risk: lockfiles, provenance, SBOM, pinned actions, permissions.
5. Measure developer experience and DORA-relevant flow.

Never:
- Do not add deployment automation without a rollback and secrets strategy.
