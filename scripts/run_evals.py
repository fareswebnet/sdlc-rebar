#!/usr/bin/env python3
"""Run skill evaluation scenarios against any OpenAI-compatible model: baseline (no skill) versus with the compact skill.

Each scenario in evals/<skill>.json has a prompt, `must` regexes (all required) and `forbid` regexes (none allowed).
Scores are deterministic string checks, a floor and not a quality judgement.

  python scripts/run_evals.py --model llama3.1 --base-url http://localhost:11434/v1
  python scripts/run_evals.py --model qwen2.5 --skill sdlc-test-driven-development --runs 3 --out evals/results/qwen2.5.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm_client  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BASE_SYSTEM = "You are a coding assistant working in a software repository."
SKILL_SYSTEM = BASE_SYSTEM + " Follow the loaded skill steps in order and respect its Never list.\n\n"


def score(reply: str, scenario: dict) -> tuple[bool, list[str]]:
    problems = [f"missing /{p}/" for p in scenario.get("must", []) if not re.search(p, reply, re.M)]
    problems += [f"forbidden /{p}/ present" for p in scenario.get("forbid", []) if re.search(p, reply, re.M)]
    return not problems, problems


def load_scenarios(only: str | None) -> list[tuple[str, dict]]:
    items = []
    for path in sorted((ROOT / "evals").glob("sdlc-*.json")):
        data = json.loads(path.read_text())
        if only and data["skill"] != only:
            continue
        items += [(data["skill"], s) for s in data["scenarios"]]
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default=llm_client.DEFAULT_BASE_URL)
    parser.add_argument("--api-key")
    parser.add_argument("--skill")
    parser.add_argument("--runs", type=int, default=1, help="repeat each scenario to see variance")
    parser.add_argument("--full-skills", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()

    rows, base_total, skill_total, count = [], 0, 0, 0
    for skill, scenario in load_scenarios(args.skill):
        path = (ROOT / "skills" / skill / "SKILL.md") if args.full_skills else (ROOT / "compact" / f"{skill}.md")
        skill_text = path.read_text()
        base_pass = skill_pass = 0
        notes = []
        for _ in range(args.runs):
            for with_skill in (False, True):
                system = SKILL_SYSTEM + skill_text if with_skill else BASE_SYSTEM
                reply = llm_client.chat([{"role": "system", "content": system}, {"role": "user", "content": scenario["prompt"]}], args.model, args.base_url, args.api_key)
                ok, problems = score(reply, scenario)
                if with_skill:
                    skill_pass += ok
                    notes += problems
                else:
                    base_pass += ok
        rows.append((skill, scenario["id"], base_pass, skill_pass, args.runs, "; ".join(sorted(set(notes)))))
        base_total += base_pass
        skill_total += skill_pass
        count += args.runs
    lines = [f"# Skill evaluation: {args.model}", "", f"Date: {dt.date.today().isoformat()}  Runs per scenario: {args.runs}  Skills: {'full' if args.full_skills else 'compact'}", "",
             "| Skill | Scenario | Baseline pass | With skill pass | Failures with skill |", "|---|---|---|---|---|"]
    lines += [f"| {s} | {i} | {b}/{n} | {w}/{n} | {notes or '-'} |" for s, i, b, w, n, notes in rows]
    lines += ["", f"Total: baseline {base_total}/{count}, with skill {skill_total}/{count}.", "",
              "String checks are a floor, not a quality judgement; read the replies for scenarios that fail."]
    report = "\n".join(lines) + "\n"
    print(report)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
