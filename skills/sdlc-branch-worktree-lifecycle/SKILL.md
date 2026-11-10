---
name: sdlc-branch-worktree-lifecycle
description: Start feature work in an isolated git worktree or branch with a clean verified baseline, and finish it with explicit options (merge locally, open a PR, keep, or discard) after tests pass, with safe cleanup. Use when starting any implementation that should not disturb the main workspace, and when implementation is complete and needs integration.
---

# SDLC Branch Worktree Lifecycle

## Purpose

Keep the main checkout safe and give every change a clean start and a deliberate ending.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Detect whether you are already in a linked worktree or the main checkout; reuse an existing isolated workspace when present.
2. Prefer the project's declared worktree location; if none, use an ignored directory (verify with `git check-ignore`) so worktree contents are never committed.
3. Create the branch and worktree, run project setup, and run the test suite to record a clean baseline. Report failures before starting rather than blaming new work later.
4. Work in small commits tied to task ids.
5. To finish: verify tests with `sdlc-verification-before-completion`, then offer exactly these options: merge locally, push and open a PR, keep as is, or discard.
6. Discard requires typed confirmation listing the branch and commits being lost. Clean up the worktree only for merge and discard.
7. Never force-push or rewrite shared history without explicit approval.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Isolated branch or worktree, baseline test record, commit history, chosen integration outcome, cleanup confirmation.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Do not start on a dirty baseline without telling the user.
- Never delete work without explicit confirmation of what is lost.
- Do not merge with failing tests.
- Keep unrelated user changes untouched.

## Runtime Fallbacks

Without worktree support, use a plain branch in a clean checkout and record the baseline test result before starting. If the tree is dirty, stop and ask before continuing. See `docs/references/runtime-capabilities.md`.

## Handoff

`sdlc-code-review-quality-gate` before merge; `sdlc-release-production-readiness` for release.

## Source Guidance

Adapted idea, extended beyond the source, not copied text: superpowers using-git-worktrees and finishing-a-development-branch. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
- `docs/references/sourcing-matrix.md`
