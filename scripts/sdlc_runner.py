#!/usr/bin/env python3
"""Minimal SDLC runner for models without skills, subagents, or tool calling (local open-source LLMs).

It loads AGENTS.md and compact skills into the system prompt, asks the model for the work, optionally applies
file blocks, then lets *scripts* be the gate: failing gate output is fed back for another round.

The model replies with files as:

    FILE: relative/path.ext
    ```
    content
    ```

Examples:
  python scripts/sdlc_runner.py --model qwen2.5-coder --skill sdlc-test-driven-development \\
      --task "Add a slugify function with tests" --workdir ./app --apply --gate "python -m unittest" --max-rounds 3
  python scripts/sdlc_runner.py --model llama3.1 --skill sdlc-spec-clarification --task-file notes.md

Safety: file writes are confined to --workdir; gate commands are the ones you pass and run without a shell.
"""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm_client  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FILE_RE = re.compile(r"^FILE:\s*(?P<path>\S+)\s*\n```[^\n]*\n(?P<body>.*?)\n```", re.M | re.S)
SYSTEM_RULES = (
    "You follow the AI SDLC method. Follow the loaded skill steps in order and respect its Never list. "
    "Do not claim work is done without evidence from the gate commands. "
    "When you create or change files, output each as 'FILE: path' followed by a fenced block."
)


def build_system(skills: list[str], workdir: Path, full: bool) -> str:
    parts = [SYSTEM_RULES]
    agents = workdir / "AGENTS.md"
    if agents.exists():
        parts.append("Repository instructions (AGENTS.md):\n" + agents.read_text())
    for name in skills:
        path = (ROOT / "skills" / name / "SKILL.md") if full else (ROOT / "compact" / f"{name}.md")
        if not path.exists():
            raise SystemExit(f"unknown skill: {name}")
        parts.append(f"Skill {name}:\n" + path.read_text())
    return "\n\n".join(parts)


def apply_files(reply: str, workdir: Path) -> list[str]:
    written = []
    root = workdir.resolve()
    for match in FILE_RE.finditer(reply):
        target = (root / match["path"]).resolve()
        if root != target and root not in target.parents:
            print(f"REFUSED: path outside workdir: {match['path']}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(match["body"] + "\n")
        written.append(str(target.relative_to(root)))
    return written


def run_gates(gates: list[str], workdir: Path) -> tuple[bool, str]:
    output, ok = [], True
    for gate in gates:
        result = subprocess.run(shlex.split(gate), cwd=workdir, capture_output=True, text=True)
        output.append(f"$ {gate}\nexit {result.returncode}\n{(result.stdout + result.stderr)[-3000:]}")
        ok = ok and result.returncode == 0
    return ok, "\n".join(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default=llm_client.DEFAULT_BASE_URL)
    parser.add_argument("--api-key")
    parser.add_argument("--skill", action="append", default=[], help="skill name (repeatable); compact version by default")
    parser.add_argument("--full-skills", action="store_true", help="load full SKILL.md instead of compact")
    parser.add_argument("--task")
    parser.add_argument("--task-file")
    parser.add_argument("--workdir", default=".")
    parser.add_argument("--apply", action="store_true", help="write FILE blocks into --workdir")
    parser.add_argument("--gate", action="append", default=[], help="command that must exit 0 (repeatable)")
    parser.add_argument("--max-rounds", type=int, default=3)
    parser.add_argument("--out", help="write the transcript here")
    args = parser.parse_args()

    task = args.task or (Path(args.task_file).read_text() if args.task_file else None)
    if not task:
        parser.error("give --task or --task-file")
    workdir = Path(args.workdir).resolve()
    messages = [{"role": "system", "content": build_system(args.skill, workdir, args.full_skills)}, {"role": "user", "content": task}]
    transcript = []
    passed = not args.gate
    for round_number in range(1, args.max_rounds + 1):
        reply = llm_client.chat(messages, args.model, args.base_url, args.api_key)
        messages.append({"role": "assistant", "content": reply})
        transcript.append(f"## Round {round_number} model reply\n\n{reply}")
        print(reply)
        if args.apply:
            written = apply_files(reply, workdir)
            transcript.append("Files written: " + (", ".join(written) or "none"))
        if not args.gate:
            break
        passed, report = run_gates(args.gate, workdir)
        transcript.append(f"## Round {round_number} gates\n\n{report}")
        print(f"--- gates round {round_number}: {'PASS' if passed else 'FAIL'}")
        if passed:
            break
        messages.append({"role": "user", "content": "The gate failed. Fix the cause (do not weaken the check) and reply with the changed files.\n\n" + report})
    if args.out:
        Path(args.out).write_text("\n\n".join(transcript) + "\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
