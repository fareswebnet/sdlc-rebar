#!/usr/bin/env python3
"""Check requirement -> scenario -> task -> test traceability in a repo-first SDLC docs tree.

Conventions (see skills/sdlc-traceability-ledger):
  requirement ids   FR-001, NFR-001, SEC-001, AI-001 defined as a heading or list item in docs/product/**/*.md
  scenarios         Gherkin/markdown files under docs/product/ tagged with @FR-001
  tasks             docs/engineering/tasks.md lines: - [ ] T001 [P] [US1] (FR-001) Action in path
  tests             files under tests/ or test/ that mention the requirement id
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ID = r"(?:FR|NFR|SEC|AI)-\d{3}"
ID_RE = re.compile(rf"\b{ID}\b")
DEF_RE = re.compile(rf"^\s*(?:[-*]\s+|#+\s+)\**({ID})\b", re.M)
TASK_RE = re.compile(r"^\s*- \[(?P<done>[ xX])\]\s+(?P<tid>T\d{3})\b(?P<rest>.*)$")
BAD_TASK_RE = re.compile(r"^\s*- \[[ xX]\]\s+(?!T\d{3}\b)")
TEXT_SUFFIXES = {".md", ".feature", ".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".kt", ".go", ".rb", ".php", ".cs", ".swift", ".yaml", ".yml", ".txt"}


def read(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except OSError:
        return ""


def collect(target: Path) -> dict:
    product = target / "docs" / "product"
    requirements: dict[str, str] = {}
    scenarios: dict[str, set[str]] = {}
    if product.exists():
        for path in sorted(product.rglob("*")):
            if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
                continue
            text = read(path)
            rel = str(path.relative_to(target))
            if path.suffix == ".md" and "bdd" not in path.parts:
                for rid in DEF_RE.findall(text):
                    requirements.setdefault(rid, rel)
            if path.suffix == ".feature" or "bdd" in path.parts:
                for rid in re.findall(rf"@({ID})\b", text):
                    scenarios.setdefault(rid, set()).add(rel)

    tasks: list[dict] = []
    format_errors: list[str] = []
    tasks_file = target / "docs" / "engineering" / "tasks.md"
    for number, line in enumerate(read(tasks_file).splitlines(), 1):
        match = TASK_RE.match(line)
        if match:
            tasks.append({"id": match["tid"], "done": match["done"] != " ", "refs": ID_RE.findall(match["rest"]), "line": number})
        elif BAD_TASK_RE.match(line):
            format_errors.append(f"docs/engineering/tasks.md:{number}: task line without T### id")

    tests: dict[str, set[str]] = {}
    for folder in ("tests", "test"):
        base = target / folder
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix in TEXT_SUFFIXES:
                for rid in set(ID_RE.findall(read(path))):
                    tests.setdefault(rid, set()).add(str(path.relative_to(target)))
    return {"requirements": requirements, "scenarios": scenarios, "tasks": tasks, "tests": tests, "format_errors": format_errors}


def analyze(data: dict) -> dict:
    reqs = data["requirements"]
    findings: list[dict] = []

    def add(severity: str, where: str, message: str) -> None:
        findings.append({"severity": severity, "where": where, "message": message})

    for error in data["format_errors"]:
        add("HIGH", error.split(": ")[0], error.split(": ", 1)[1])
    seen: dict[str, int] = {}
    for task in data["tasks"]:
        if task["id"] in seen:
            add("HIGH", f"tasks.md:{task['line']}", f"duplicate task id {task['id']} (first at line {seen[task['id']]})")
        seen.setdefault(task["id"], task["line"])
        for ref in task["refs"]:
            if ref not in reqs:
                add("HIGH", f"tasks.md:{task['line']}", f"{task['id']} references unknown requirement {ref}")
        if not task["refs"]:
            add("LOW", f"tasks.md:{task['line']}", f"{task['id']} has no requirement reference (fine for setup and polish)")
    for rid in sorted(data["scenarios"]):
        if rid not in reqs:
            add("HIGH", ", ".join(sorted(data["scenarios"][rid])), f"scenario tagged with unknown requirement {rid}")

    matrix = []
    for rid in sorted(reqs):
        task_ids = [t["id"] for t in data["tasks"] if rid in t["refs"]]
        done = [t["id"] for t in data["tasks"] if rid in t["refs"] and t["done"]]
        row = {
            "requirement": rid,
            "defined_in": reqs[rid],
            "scenarios": sorted(data["scenarios"].get(rid, [])),
            "tasks": task_ids,
            "tests": sorted(data["tests"].get(rid, [])),
        }
        matrix.append(row)
        if not row["scenarios"]:
            add("HIGH", rid, "no BDD scenario tagged for this requirement")
        if not task_ids:
            add("HIGH", rid, "no task implements this requirement")
        if done and not row["tests"]:
            add("MEDIUM", rid, f"tasks {', '.join(done)} done but no test mentions {rid}")
    covered = sum(1 for r in matrix if r["scenarios"] and r["tasks"])
    metrics = {
        "requirements": len(reqs),
        "fully_covered": covered,
        "coverage_percent": round(100 * covered / len(reqs), 1) if reqs else 0.0,
        "tasks": len(data["tasks"]),
        "high": sum(1 for f in findings if f["severity"] == "HIGH"),
        "medium": sum(1 for f in findings if f["severity"] == "MEDIUM"),
    }
    return {"matrix": matrix, "findings": findings, "metrics": metrics}


def render(result: dict) -> str:
    lines = ["| Requirement | Scenarios | Tasks | Tests |", "|---|---|---|---|"]
    for row in result["matrix"]:
        lines.append(f"| {row['requirement']} | {len(row['scenarios'])} | {', '.join(row['tasks']) or '-'} | {len(row['tests'])} |")
    lines.append("")
    for finding in sorted(result["findings"], key=lambda f: ["HIGH", "MEDIUM", "LOW"].index(f["severity"])):
        lines.append(f"[{finding['severity']}] {finding['where']}: {finding['message']}")
    metrics = result["metrics"]
    lines.append("")
    lines.append(f"coverage {metrics['coverage_percent']}% ({metrics['fully_covered']}/{metrics['requirements']}), tasks {metrics['tasks']}, high {metrics['high']}, medium {metrics['medium']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", default=".", help="Repository root containing docs/")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    parser.add_argument("--strict", action="store_true", help="Fail on MEDIUM findings too")
    args = parser.parse_args()
    result = analyze(collect(Path(args.target).expanduser().resolve()))
    print(json.dumps(result, indent=2) if args.json else render(result))
    metrics = result["metrics"]
    return 1 if metrics["high"] or (args.strict and metrics["medium"]) else 0


if __name__ == "__main__":
    sys.exit(main())
