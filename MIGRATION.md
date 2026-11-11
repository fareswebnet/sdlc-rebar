# Migration notes

## 0.4.0

Skill renames (the `sdlc-` prefix is kept). Reinstall and delete the old folders from your skills directory (`~/.claude/skills`, `~/.codex/skills`, `.agents/skills`, ...), otherwise both versions stay installed.

| Old | New |
|---|---|
| `sdlc-delivery-system` | `sdlc-delivery-orchestrator` |
| `sdlc-code-review-quality-gate` | `sdlc-code-review` |
| `sdlc-code-review-reception` | `sdlc-receiving-code-review` |
| `sdlc-data-database-architecture` | `sdlc-data-architecture` |
| `sdlc-quality-test-strategy` | `sdlc-test-strategy` |
| `sdlc-devops-ci-cd-platform` | `sdlc-ci-cd-platform` |
| `sdlc-documentation-knowledge` | `sdlc-documentation` |
| `sdlc-ai-assisted-development` | `sdlc-ai-coding-governance` |
| `sdlc-performance-scalability-cost` | `sdlc-scalability-cost` |
| `sdlc-system-merge-convergence` | `sdlc-system-merge` |
| `sdlc-product-analytics-experimentation` | `sdlc-product-analytics` |

Removed (no measured gain, see `docs/references/skill-value-analysis.md`): `sdlc-product-strategy` (use `sdlc-idea-framing`), `sdlc-api-integration-contracts` (use `sdlc-api-versioning-deprecation`), `sdlc-identity-access-multitenancy` (use `sdlc-security-privacy-compliance`), `sdlc-release-production-readiness` (use `sdlc-definition-of-done`), `sdlc-technical-debt-evolution` (use `sdlc-delivery-retrospective`), `sdlc-maturity-assessment`, `sdlc-skill-authoring` (use `sdlc-skill-evaluation`).

Other changes:

- `--native-roles` now writes `.claude/agents/sdlc-<role>.md`; delete the old unprefixed files.
- `presets/preset-<name>.md` is now `presets/<name>.md`.
