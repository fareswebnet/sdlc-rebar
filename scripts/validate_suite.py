#!/usr/bin/env python3
"""Validate AI SDLC skill folders."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REQUIRED = {"name", "description"}
BAD = re.compile(r"TODO|TBD|FIXME|placeholder|A COMPLETER|a completer", re.I)


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing opening frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing closing frontmatter")
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


def main() -> int:
    errors: list[str] = []
    for skill in sorted(SKILLS.glob("sdlc-*")):
        skill_md = skill / "SKILL.md"
        openai = skill / "agents" / "openai.yaml"
        if not skill_md.exists():
            errors.append(f"{skill.name}: missing SKILL.md")
            continue
        if not openai.exists():
            errors.append(f"{skill.name}: missing agents/openai.yaml")
        text = skill_md.read_text()
        try:
            fields = parse_frontmatter(text)
        except ValueError as exc:
            errors.append(f"{skill.name}: {exc}")
            continue
        missing = REQUIRED - set(fields)
        if missing:
            errors.append(f"{skill.name}: missing {', '.join(sorted(missing))}")
        if fields.get("name") != skill.name:
            errors.append(f"{skill.name}: frontmatter name mismatch")
        if len(fields.get("description", "")) < 80:
            errors.append(f"{skill.name}: description too short")
        if BAD.search(text):
            errors.append(f"{skill.name}: contains placeholder text")
    count = len(list(SKILLS.glob("sdlc-*")))
    if count != 33:
        errors.append(f"expected 33 skills, found {count}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: validated {count} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
