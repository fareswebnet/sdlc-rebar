#!/usr/bin/env python3
"""Install the AI SDLC suite for Codex, Claude Code, Antigravity, or any other agent runtime.

Skills go where each runtime discovers them. The only repository memory file is AGENTS.md, written as a
managed block (re-running replaces the block and never touches the rest of the file).

Examples:
  python scripts/install.py --runtime claude --target ~/work/app --agents-md --with-kit
  python scripts/install.py --runtime codex --scope user
  python scripts/install.py --runtime antigravity --target . --agents-md --roles
  python scripts/install.py --runtime generic --target . --agents-md --dry-run
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

SUITE = Path(__file__).resolve().parents[1]
KIT_DIRS = ["harnesses", "pipelines", "agents", "presets", "scripts", "templates", "data", "docs/references"]
BLOCK = ("<!-- sdlc:begin -->", "<!-- sdlc:end -->")
ROLES = ("<!-- sdlc-roles:begin -->", "<!-- sdlc-roles:end -->")


def skills_dest(runtime: str, scope: str, target: Path, home: Path) -> Path:
    if scope == "user":
        table = {"codex": home / ".codex" / "skills", "claude": home / ".claude" / "skills", "antigravity": home / ".gemini" / "config" / "skills"}
        if runtime not in table:
            raise SystemExit("generic runtime has no user-level skills folder; use --scope project")
        return table[runtime]
    return target / (".claude/skills" if runtime == "claude" else ".agents/skills")


def parse_role(path: Path) -> dict:
    data: dict = {"id": path.stem, "lists": {}}
    current = None
    for line in path.read_text().splitlines():
        top = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if top:
            current = top.group(1)
            if top.group(2):
                data[current] = top.group(2)
            else:
                data["lists"][current] = []
        elif current and (item := re.match(r"^\s+- (.+)$", line)):
            data["lists"].setdefault(current, []).append(item.group(1))
    return data


def render_roles() -> str:
    lines = ["## Agent roles", "", "Adopt the role that matches the task; respect its gates and hand off as listed. If your runtime supports subagents, run a role as one; otherwise follow the role in sequence in separate sessions.", ""]
    for path in sorted((SUITE / "agents").glob("*.yaml")):
        role = parse_role(path)
        lines.append(f"### {role.get('name', role['id'])} (`{role['id']}`)")
        lines.append(f"{role.get('purpose', '')}")
        for label, key in (("Skills", "skills"), ("Gates", "gates"), ("Hands off to", "handoffs")):
            values = role["lists"].get(key, [])
            if values:
                lines.append(f"- {label}: " + ("; ".join(values) if key == "gates" else ", ".join(f"`{v}`" for v in values)))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def upsert_block(text: str, markers: tuple[str, str], body: str) -> str:
    block = f"{markers[0]}\n{body.rstrip()}\n{markers[1]}"
    pattern = re.compile(re.escape(markers[0]) + r".*?" + re.escape(markers[1]), re.S)
    if pattern.search(text):
        return pattern.sub(lambda _m: block, text, count=1)
    separator = "" if not text or text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
    return text + separator + block + "\n"


def write(path: Path, content: str, dry: bool) -> None:
    print(f"{'would write' if dry else 'write'} {path}")
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runtime", required=True, choices=["codex", "claude", "antigravity", "generic"])
    parser.add_argument("--scope", choices=["project", "user"], default="project")
    parser.add_argument("--target", default=".", help="Target repository (project scope and AGENTS.md)")
    parser.add_argument("--mode", choices=["copy", "link"], default="copy")
    parser.add_argument("--with-kit", action="store_true", help="Copy harnesses, scripts, agents, docs into <target>/.sdlc so skills can reference them")
    parser.add_argument("--agents-md", action="store_true", help="Write or update the managed block in <target>/AGENTS.md")
    parser.add_argument("--roles", action="store_true", help="Render agent roles into AGENTS.md")
    parser.add_argument("--native-roles", action="store_true", help="Claude only: also write .claude/agents/*.md subagents")
    parser.add_argument("--force", action="store_true", help="Overwrite existing skill folders")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--home", default=str(Path.home()), help=argparse.SUPPRESS)
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    dest = skills_dest(args.runtime, args.scope, target, Path(args.home))
    installed = skipped = 0
    for skill in sorted((SUITE / "skills").glob("sdlc-*")):
        out = dest / skill.name
        if out.exists() or out.is_symlink():
            if not args.force:
                skipped += 1
                continue
            if not args.dry_run:
                shutil.rmtree(out) if out.is_dir() and not out.is_symlink() else out.unlink()
        print(f"{'would ' if args.dry_run else ''}{args.mode} {skill.name} -> {out}")
        if not args.dry_run:
            out.parent.mkdir(parents=True, exist_ok=True)
            if args.mode == "link":
                out.symlink_to(skill)
            else:
                shutil.copytree(skill, out)
        installed += 1
    print(f"skills: {installed} installed, {skipped} skipped (use --force to overwrite) in {dest}")

    kit = str(SUITE)
    if args.with_kit:
        kit = ".sdlc"
        for name in KIT_DIRS:
            src = SUITE / name
            print(f"{'would copy' if args.dry_run else 'copy'} {name} -> {target / '.sdlc' / name}")
            if not args.dry_run:
                shutil.copytree(src, target / ".sdlc" / name, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))

    if args.agents_md:
        agents_md = target / "AGENTS.md"
        text = agents_md.read_text() if agents_md.exists() else "# AGENTS.md\n"
        body = (SUITE / "templates" / "AGENTS.md").read_text().replace("{{KIT}}", kit)
        text = upsert_block(text, BLOCK, body)
        if args.roles:
            text = upsert_block(text, ROLES, render_roles())
        write(agents_md, text, args.dry_run)

    if args.native_roles:
        if args.runtime != "claude":
            raise SystemExit("--native-roles is only available for --runtime claude")
        for path in sorted((SUITE / "agents").glob("*.yaml")):
            role = parse_role(path)
            body = [f"---", f"name: sdlc-{role['id']}", f"description: {role.get('purpose', role['id'])}", "---", "",
                    f"You are the {role.get('name', role['id'])} role of the AI SDLC suite.", "",
                    "Use these skills: " + ", ".join(role["lists"].get("skills", [])) + ".", "", "Gates:"]
            body += [f"- {g}" for g in role["lists"].get("gates", [])]
            body += ["", "Hand off to: " + ", ".join("sdlc-" + h for h in role["lists"].get("handoffs", [])) + "."]
            write(target / ".claude" / "agents" / f"sdlc-{role['id']}.md", "\n".join(body) + "\n", args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
