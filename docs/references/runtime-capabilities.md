# Runtime Capabilities And Fallbacks

The suite assumes no particular runtime. Skills describe what to do; this page says what to do when a capability is missing. Repository memory is always a single `AGENTS.md`.

| Capability | Codex | Claude Code | Antigravity | Local open-source LLM |
|---|---|---|---|---|
| Skill discovery by description | yes | yes | yes | no: use `scripts/skill_index.py` |
| Project skills folder | `.agents/skills` | `.claude/skills` | `.agents/skills` | any folder you load from |
| Repo memory file | `AGENTS.md` | `AGENTS.md` imported from a one-line `CLAUDE.md` if the runtime requires it | `AGENTS.md` | pasted into the system prompt |
| Subagents | yes | yes | yes | no: run roles as separate sessions |
| Worktrees | via git | via git | via git | via git commands you run |
| MCP connectors | yes | yes | yes | usually no |
| Shell and scripts | yes | yes | yes | needs a tool-calling harness |

## Fallbacks

| Missing | Fallback |
|---|---|
| Subagents | Run tasks sequentially. Run each review (spec compliance, code quality, independent verification) in a new session that receives only the brief, the diff, and the registry, never the implementer's history. |
| Worktrees | Use a branch in a clean checkout; if the working tree is dirty, stop and ask. |
| MCP or tracker access | Export the task list and issue bodies as Markdown for a human to paste; never invent issue numbers. |
| Skill discovery | Put `python scripts/skill_index.py` output in the system prompt, then load the selected skill with `--skill <name>`. |
| Reliable instruction following (small models) | Prefer scripts as gates: `scripts/sdlc_trace.py`, `scripts/sdlc_registry.py`, and test commands. Give one skill at a time and the exact next step. |
| Long context | Load only the skill, the current task, and the relevant spec excerpt; keep `AGENTS.md` short. |

## Independence rule across runtimes

Verification and review must run in a context that does not contain the implementer's reasoning. With one model, that means a new session; with several, use a different model for the verifier.
