#!/usr/bin/env python3
"""Scaffold repo-first SDLC documentation templates into a target project."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_tree(src: Path, dst: Path, force: bool) -> tuple[int, int]:
    copied = 0
    skipped = 0
    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not force:
            skipped += 1
            continue
        shutil.copy2(path, target)
        copied += 1
    return copied, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy SDLC docs templates into a target repo.")
    parser.add_argument("--target", required=True, help="Target repository or project directory")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    script = Path(__file__).resolve()
    repo_root = script.parents[3]
    templates = repo_root / "templates" / "docs"
    target = Path(args.target).expanduser().resolve() / "docs"

    if not templates.exists():
        raise SystemExit(f"Templates not found: {templates}")
    copied, skipped = copy_tree(templates, target, args.force)
    print(f"Scaffolded SDLC docs into {target}")
    print(f"Copied: {copied}")
    print(f"Skipped existing: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
