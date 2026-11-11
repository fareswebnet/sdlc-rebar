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

## Compact skills

`compact/<skill>.md` holds a shortened version of every skill (about half the size: when, goal, steps, never, next), regenerated with `python scripts/compact_skills.py` and checked in CI. Use them for small context windows; load the full `SKILL.md` for large models.

## Minimal runner

`scripts/sdlc_runner.py` drives any OpenAI-compatible endpoint (Ollama, vLLM, llama.cpp server, LM Studio). It puts `AGENTS.md` and the chosen compact skills in the system prompt, applies `FILE:` blocks inside `--workdir`, and lets scripts be the gate: a failing gate command is fed back for another round.

```bash
python scripts/sdlc_runner.py --model qwen2.5-coder --skill sdlc-test-driven-development \
  --task "Add a slugify function with tests" --workdir ./app --apply \
  --gate "python -m unittest" --max-rounds 3 --out run.md
```

File writes cannot leave `--workdir`, and gate commands run without a shell.

## Measuring a model

```bash
python scripts/run_evals.py --model qwen2.5-coder --runs 3 --out evals/results/qwen2.5-coder.md
```

See `evals/README.md`. Run it on each model you plan to use before trusting it with gates.

## Small-model guidance

- Let scripts enforce gates: `sdlc_trace.py`, `sdlc_registry.py`, and the project's test commands.
- Keep context small: the skill, the task, and the relevant spec excerpt only.
- Run review and verification in a new conversation containing only the brief and the diff.
- Prefer a stronger model for verification and design review, and a smaller one for mechanical tasks.
- Without tool calling, have the model output commands and file contents for a human or a thin wrapper to apply.

See `docs/references/runtime-capabilities.md` for fallbacks per missing capability.
