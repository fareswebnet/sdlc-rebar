#!/usr/bin/env python3
"""List, search, or print skills for runtimes without native skill discovery (for example local open-source LLMs).

  python scripts/skill_index.py                        # markdown index to paste into a system prompt
  python scripts/skill_index.py --format json
  python scripts/skill_index.py --select "migrate legacy system" --top 3
  python scripts/skill_index.py --skill sdlc-task-breakdown    # print the full SKILL.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "skills"


def load() -> list[dict]:
    items = []
    for path in sorted(SKILLS.glob("sdlc-*/SKILL.md")):
        text = path.read_text()
        name = re.search(r"^name:\s*(.+)$", text, re.M)
        desc = re.search(r"^description:\s*(.+)$", text, re.M)
        items.append({"name": name.group(1).strip(), "description": desc.group(1).strip() if desc else "", "path": str(path)})
    return items


def score(query: str, item: dict) -> int:
    words = set(re.findall(r"[a-z0-9]+", query.lower()))
    haystack = set(re.findall(r"[a-z0-9]+", (item["name"] + " " + item["description"]).lower()))
    return len(words & haystack)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--select", help="keyword query; prints the best matching skills")
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--skill", help="print the full SKILL.md of one skill")
    args = parser.parse_args()
    items = load()
    if args.skill:
        match = next((i for i in items if i["name"] == args.skill), None)
        if not match:
            print(f"unknown skill {args.skill}", file=sys.stderr)
            return 1
        print(Path(match["path"]).read_text())
        return 0
    if args.select:
        ranked = sorted(items, key=lambda i: -score(args.select, i))
        items = [i for i in ranked[: args.top] if score(args.select, i) > 0]
    if args.format == "json":
        print(json.dumps([{k: v for k, v in i.items() if k != "path"} for i in items], indent=2))
    else:
        for item in items:
            print(f"- {item['name']}: {item['description']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
