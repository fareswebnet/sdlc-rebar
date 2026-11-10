# Antigravity (Gemini) Integration

Antigravity discovers skills from `SKILL.md` folders and plugins that carry a `plugin.json`.

## Install

As a plugin: place this repository (or a clone) where Antigravity loads plugins; the root `plugin.json` and `skills/` folder are discovered.

For one project, with the installer:

```bash
python scripts/install.py --runtime antigravity --target /path/to/repo --agents-md --with-kit
```

For all your projects:

```bash
python scripts/install.py --runtime antigravity --scope user
```

## Repository memory

Only `AGENTS.md` is needed. `--agents-md` writes a managed block (between `sdlc:begin` and `sdlc:end` markers) and leaves the rest of the file alone; re-running updates the block. Add `--roles` to render the agent roles into the same file.

## Using the suite

- Mention the skill by name: `use sdlc-spec-clarification on docs/product/prd.md`.
- Run a harness: `follow harnesses/spec-driven-delivery.yaml for this feature`.
- Subagents: run a role from `agents/` as a subagent; if you cannot, follow `docs/references/runtime-capabilities.md`.

## Safety

Use planning or read-only mode for architecture, security, and production tasks, and require approval for dependency changes, secrets, migrations, tracker writes, and deployments.
