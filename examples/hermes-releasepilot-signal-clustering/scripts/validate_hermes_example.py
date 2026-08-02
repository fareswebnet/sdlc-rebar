#!/usr/bin/env python3
"""Validate the Hermes ReleasePilot example."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BAD_MARKERS = [
    "TO" + "DO",
    "T" + "BD",
    "FIX" + "ME",
    "place" + "holder",
    "A " + "COMPLETER",
    "a " + "completer",
]
BAD = re.compile("|".join(re.escape(marker) for marker in BAD_MARKERS), re.I)

REQUIRED_FILES = [
    "README.md",
    "hermes/.hermes.md",
    "hermes/profile.releasepilot.yaml",
    "hermes/memory-seed.md",
    "artifacts/task-graph.yaml",
    "artifacts/signal-clustering-sdlc-map.md",
    "artifacts/bdd-scenarios.feature",
    "artifacts/red-tests.md",
    "artifacts/feature-flag.yaml",
    "artifacts/implementation-plan.md",
    "artifacts/simulated-pr.md",
    "artifacts/review-gate.md",
    "artifacts/production-follow-up.md",
    "prompts/hermes-kickoff.md",
    "prompts/hermes-stage-handoff.md",
    "prompts/hermes-nightly-followup.md",
]

REQUIRED_SKILLS = [
    "releasepilot-research",
    "releasepilot-domain",
    "releasepilot-bdd",
    "releasepilot-architecture",
    "releasepilot-tdd",
    "releasepilot-implementation",
    "releasepilot-security-review",
    "releasepilot-pr-review",
    "releasepilot-roi",
]


def read(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"{path.relative_to(ROOT)} is missing")
        return ""
    text = path.read_text()
    if BAD.search(text):
        errors.append(f"{path.relative_to(ROOT)} contains unfinished marker text")
    return text


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        read(ROOT / rel, errors)

    for skill in REQUIRED_SKILLS:
        text = read(ROOT / "skills" / skill / "SKILL.md", errors)
        if text and f"name: {skill}" not in text:
            errors.append(f"skills/{skill}/SKILL.md has a frontmatter name mismatch")
        if text and "description:" not in text:
            errors.append(f"skills/{skill}/SKILL.md is missing description")

    graph = read(ROOT / "artifacts" / "task-graph.yaml", errors)
    for required in [
        "runtime: hermes",
        "profile: releasepilot",
        "project_skill: releasepilot-tdd",
        "project_skill: releasepilot-implementation",
        "stop_condition: PR ready for human review; no production deployment and no customer communication.",
    ]:
        if graph and required not in graph:
            errors.append(f"artifacts/task-graph.yaml missing {required}")

    bdd = read(ROOT / "artifacts" / "bdd-scenarios.feature", errors)
    for required in [
        "Scenario: Similar support signals produce one candidate cluster",
        "Scenario: Tenant isolation protects signal data",
        "no product spec is generated yet",
    ]:
        if bdd and required not in bdd:
            errors.append(f"artifacts/bdd-scenarios.feature missing {required}")

    red = read(ROOT / "artifacts" / "red-tests.md", errors)
    for required in ["clusterSignals", "generateSpecDraft", "getClusterForTenant"]:
        if red and required not in red:
            errors.append(f"artifacts/red-tests.md missing {required}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"OK: validated Hermes ReleasePilot example with {len(REQUIRED_SKILLS)} project skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
