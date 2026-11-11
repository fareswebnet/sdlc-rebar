#!/usr/bin/env python3
"""Generate compact versions of every skill for small context windows.

Writes compact/<skill>.md (purpose, shortened workflow, shortened guardrails, handoff) and compact/INDEX.md.
  python scripts/compact_skills.py            # regenerate
  python scripts/compact_skills.py --check    # exit 1 if compact/ is out of date
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "compact"


def section(text: str, title: str) -> str:
    match = re.search(rf"^## {re.escape(title)}\n\n(.*?)(?=\n## |\Z)", text, re.S | re.M)
    return match.group(1).strip() if match else ""


def shorten(line: str, limit: int) -> str:
    line = re.sub(r"\s+", " ", line).strip()
    first = re.split(r"(?<=[.])\s", line, maxsplit=1)[0]
    first = first if len(first) >= 20 else line
    if len(first) <= limit:
        return first
    cut = first[:limit].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "…"


def compact(skill_md: Path) -> str:
    text = skill_md.read_text()
    name = re.search(r"^name:\s*(.+)$", text, re.M).group(1).strip()
    desc = re.search(r"^description:\s*(.+)$", text, re.M).group(1).strip()
    steps = [re.sub(r"^\d+\.\s*", "", l) for l in section(text, "Workflow").splitlines() if re.match(r"^\d+\.", l)]
    rules = [l[2:] for l in section(text, "Guardrails").splitlines() if l.startswith("- ")]
    out = [f"# {name} (compact)", "", f"When: {shorten(desc, 220)}", "", f"Goal: {shorten(section(text, 'Purpose'), 200)}", "", "Steps:"]
    out += [f"{i}. {shorten(s, 130)}" for i, s in enumerate(steps, 1)]
    out += ["", "Never:"] + [f"- {shorten(r, 110)}" for r in rules]
    handoff = section(text, "Handoff")
    if handoff:
        out += ["", f"Next: {shorten(handoff, 160)}"]
    return "\n".join(out) + "\n"


def build() -> dict[str, str]:
    files = {}
    index = ["# Compact skill index", ""]
    for path in sorted((ROOT / "skills").glob("sdlc-*/SKILL.md")):
        name = path.parent.name
        files[f"{name}.md"] = compact(path)
        desc = re.search(r"^description:\s*(.+)$", path.read_text(), re.M).group(1).strip()
        index.append(f"- {name}: {shorten(desc, 150)}")
    files["INDEX.md"] = "\n".join(index) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = build()
    if args.check:
        stale = [n for n, c in files.items() if not (OUT / n).exists() or (OUT / n).read_text() != c]
        stale += [p.name for p in OUT.glob("*.md") if p.name not in files] if OUT.exists() else []
        for name in stale:
            print(f"STALE: compact/{name}")
        return 1 if stale else 0
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.md"):
        old.unlink()
    for name, content in files.items():
        (OUT / name).write_text(content)
    print(f"wrote {len(files)} files to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
