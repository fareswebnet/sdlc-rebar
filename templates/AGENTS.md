## AI SDLC method

This repository uses the AI SDLC suite (kit location: `{{KIT}}`). Skills are named `sdlc-*`; invoke them by name in your runtime (for example `$sdlc-task-breakdown` in Codex, `/sdlc-task-breakdown` in Claude Code, or "use the sdlc-task-breakdown skill" anywhere else).

### Always
- Before coding, make expected behavior, affected architecture and data boundaries, validation commands, and rollback notes explicit.
- Write a failing test before behavior changes, and show fresh evidence before saying work is done (`sdlc-test-driven-development`, `sdlc-verification-before-completion`).
- Work in an isolated branch or worktree (`sdlc-branch-worktree-lifecycle`).
- Keep requirement ids (`FR-001`, `NFR-001`, `SEC-001`, `AI-001`) in specs, scenarios, tasks, and tests; check with `python {{KIT}}/scripts/sdlc_trace.py --target .`.

### Pick the workflow
- New product: `{{KIT}}/harnesses/app-idea-to-production.yaml`
- Feature: `{{KIT}}/harnesses/feature-to-production.yaml`
- Traceable, test-first, evidence-gated delivery: `{{KIT}}/harnesses/spec-driven-delivery.yaml`
- Legacy replacement: `{{KIT}}/harnesses/legacy-migration.yaml`; merging two systems: `{{KIT}}/harnesses/system-merge.yaml`
- Incident or production signal: `{{KIT}}/harnesses/production-feedback-loop.yaml`
- Depth by risk: `{{KIT}}/docs/references/depth-matrix.md`

### Human approval is required for
Product scope, durable architecture choices, dependency additions, secrets, customer data, payments, destructive migrations, issue-tracker writes, and production deployment.

### If your runtime lacks a tool
See `{{KIT}}/docs/references/runtime-capabilities.md` for fallbacks (no subagents, no worktrees, no MCP).
