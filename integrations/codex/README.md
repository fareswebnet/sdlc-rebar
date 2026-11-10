# Codex Integration

Use Codex as a repo-first executor for planning, implementation, review, worktrees, hooks, and scripted checks.

## Install Skills

For personal use:

```bash
python scripts/install.py --runtime codex --scope user
```

For repo-scoped use (skills, kit, and `AGENTS.md` block):

```bash
python scripts/install.py --runtime codex --target /path/to/repo --agents-md --with-kit
```

Codex invokes skills with `$sdlc-<name>`; the per-skill `agents/openai.yaml` supplies display metadata.

## Project Instructions

Add an `AGENTS.md` at the target repo root:

```md
# AGENTS.md

Use the AI SDLC skills for product, architecture, BDD, implementation, quality, security, release, and production work.

Before coding, make expected behavior, affected architecture and data boundaries, validation commands, and rollback notes explicit.

For autonomous work, follow:
- `harnesses/app-idea-to-production.yaml` for greenfield products
- `harnesses/feature-to-production.yaml` for feature work
- `harnesses/spec-driven-delivery.yaml` for traceable, test-first, evidence-gated delivery
- `harnesses/legacy-migration.yaml` and `harnesses/system-merge.yaml` for registry-driven migrations and merges
- `harnesses/production-feedback-loop.yaml` for incidents and production signals
```

## Interactive Flow

```text
Use sdlc-delivery-system.
Run the app-idea-to-production harness for this idea:
<idea>
Create the product docs, architecture plan, implementation plan, then implement the first vertical slice in a worktree.
Stop before production deployment.
```

## Scripted Flow

Use `codex exec` for deterministic stages in CI or local scripts:

```bash
codex exec --sandbox workspace-write \
  "Use sdlc-code-review-quality-gate to review the current diff against docs/product/prd.md and docs/product/bdd."
```

Keep scripted runs narrow. Use separate runs for product docs, architecture review, implementation, QA, and code review when context would otherwise become noisy.

## Hooks

Recommended project hooks:

- block edits to secrets and production config unless explicitly approved
- run formatters or validation commands after code edits
- capture final validation summaries into CI artifacts
- notify when a long-running run needs human input

Hooks should enforce deterministic policy. Do not encode product judgment in hooks.

## Worktrees

Use worktrees for parallel builder, QA, and review work:

- one branch or worktree per vertical slice
- no shared uncommitted state between agents
- PR remains the source of truth for review and merge

## Safety Defaults

- docs and tests can usually be edited autonomously
- production deploy, destructive migrations, dependency additions, secrets, and billing changes require explicit human approval
- keep global instructions short; keep project-specific behavior in `AGENTS.md`
