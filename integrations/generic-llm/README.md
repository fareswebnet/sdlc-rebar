# Generic And Open-Source LLM Integration

For runtimes without skill discovery (local models served by Ollama, vLLM, llama.cpp, or any chat API), the suite works as text plus scripts.

## Setup

```bash
python scripts/install.py --runtime generic --target /path/to/repo --agents-md --roles --with-kit
```

This writes skills to `.agents/skills`, the kit to `.sdlc/`, and a managed block in `AGENTS.md`. Paste `AGENTS.md` into the system prompt (or load it through your harness).

## Selecting skills

```bash
python scripts/skill_index.py                                   # one-line index for the system prompt
python scripts/skill_index.py --select "migrate legacy system"  # best matches by keyword
python scripts/skill_index.py --skill sdlc-task-breakdown       # full skill text to load
```

Load one skill at a time and state the exact next step.

## Small-model guidance

- Let scripts enforce gates: `sdlc_trace.py`, `sdlc_registry.py`, and the project's test commands.
- Keep context small: the skill, the task, and the relevant spec excerpt only.
- Run review and verification in a new conversation containing only the brief and the diff.
- Prefer a stronger model for verification and design review, and a smaller one for mechanical tasks.
- Without tool calling, have the model output commands and file contents for a human or a thin wrapper to apply.

See `docs/references/runtime-capabilities.md` for fallbacks per missing capability.
