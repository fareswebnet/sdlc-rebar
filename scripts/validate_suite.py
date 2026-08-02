#!/usr/bin/env python3
"""Validate AI SDLC skill folders."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
AGENTS = ROOT / "agents"
HARNESSES = ROOT / "harnesses"
PIPELINES = ROOT / "pipelines"
INTEGRATIONS = ROOT / "integrations"
EXAMPLES = ROOT / "examples"
REQUIRED = {"name", "description"}
BAD = re.compile(r"TODO|TBD|FIXME|placeholder|A COMPLETER|a completer", re.I)
EXPECTED_AGENTS = {
    "orchestrator",
    "product-strategist",
    "domain-architect",
    "ux-ui-designer",
    "solution-architect",
    "fullstack-builder",
    "qa-test-engineer",
    "security-reviewer",
    "devops-sre",
    "code-reviewer",
    "release-manager",
}
EXPECTED_HARNESSES = {
    "app-idea-to-production",
    "feature-to-production",
    "production-feedback-loop",
}
EXPECTED_PIPELINES = {
    "idea-to-pr.md",
    "pr-to-production.md",
    "production-feedback-loop.md",
}
EXPECTED_INTEGRATIONS = {
    "codex",
    "claude-code",
    "hermes",
    "openclaw",
    "github-actions",
    "mcp",
}
EXPECTED_EXAMPLE_FILES = {
    "fintech-cfo-b2b/sdlc-case-study.md",
    "agent-factory-idea-to-pr/README.md",
    "agent-factory-idea-to-pr/artifacts/task-graph.yaml",
    "agent-factory-idea-to-pr/artifacts/sdlc-artifact-map.md",
    "agent-factory-idea-to-pr/artifacts/simulated-pr.md",
    "agent-factory-idea-to-pr/artifacts/review-gate.md",
    "agent-factory-idea-to-pr/prompts/codex.md",
    "agent-factory-idea-to-pr/prompts/claude-code.md",
    "agent-factory-idea-to-pr/prompts/hermes.md",
}


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


def read_checked(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"{path.relative_to(ROOT)}: missing")
        return ""
    text = path.read_text()
    if BAD.search(text):
        errors.append(f"{path.relative_to(ROOT)}: contains placeholder text")
    return text


def require_keys(path: Path, text: str, keys: set[str], errors: list[str]) -> None:
    for key in sorted(keys):
        if not re.search(rf"^{re.escape(key)}:", text, re.M):
            errors.append(f"{path.relative_to(ROOT)}: missing key {key}")


def validate_references(path: Path, text: str, known_skills: set[str], known_agents: set[str], errors: list[str]) -> None:
    for skill in sorted(set(re.findall(r"^\s+- (sdlc-[a-z0-9-]+)\s*$", text, re.M))):
        if skill not in known_skills:
            errors.append(f"{path.relative_to(ROOT)}: unknown skill {skill}")
    for agent in sorted(set(re.findall(r"^\s+agent: ([a-z0-9-]+)\s*$", text, re.M))):
        if agent not in known_agents:
            errors.append(f"{path.relative_to(ROOT)}: unknown agent {agent}")


def validate_example_files(known_skills: set[str], errors: list[str]) -> None:
    for example_file in sorted(EXPECTED_EXAMPLE_FILES):
        path = EXAMPLES / example_file
        text = read_checked(path, errors)
        if example_file.endswith(".yaml"):
            validate_references(path, text, known_skills, EXPECTED_AGENTS, errors)
    task_graph = read_checked(EXAMPLES / "agent-factory-idea-to-pr" / "artifacts" / "task-graph.yaml", errors)
    for required in ("source_harness: harnesses/app-idea-to-production.yaml", "stop_condition:", "completion:"):
        if required not in task_graph:
            errors.append(f"examples/agent-factory-idea-to-pr/artifacts/task-graph.yaml: missing {required}")
    simulated_pr = read_checked(EXAMPLES / "agent-factory-idea-to-pr" / "artifacts" / "simulated-pr.md", errors)
    for required in ("## Summary", "## Tests", "## Security And Privacy", "## Human Gate"):
        if required not in simulated_pr:
            errors.append(f"examples/agent-factory-idea-to-pr/artifacts/simulated-pr.md: missing {required}")


def main() -> int:
    errors: list[str] = []
    known_skills = {path.name for path in SKILLS.glob("sdlc-*")}
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

    known_agents = {path.stem for path in AGENTS.glob("*.yaml")}
    if known_agents != EXPECTED_AGENTS:
        missing = EXPECTED_AGENTS - known_agents
        extra = known_agents - EXPECTED_AGENTS
        if missing:
            errors.append(f"missing agents: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"unexpected agents: {', '.join(sorted(extra))}")
    for agent_path in sorted(AGENTS.glob("*.yaml")):
        text = read_checked(agent_path, errors)
        require_keys(
            agent_path,
            text,
            {"id", "name", "purpose", "recommended_runtimes", "skills", "outputs", "permissions", "gates", "handoffs"},
            errors,
        )
        if not re.search(rf"^id: {re.escape(agent_path.stem)}$", text, re.M):
            errors.append(f"{agent_path.relative_to(ROOT)}: id mismatch")
        validate_references(agent_path, text, known_skills, EXPECTED_AGENTS, errors)

    known_harnesses = {path.stem for path in HARNESSES.glob("*.yaml")}
    if known_harnesses != EXPECTED_HARNESSES:
        missing = EXPECTED_HARNESSES - known_harnesses
        extra = known_harnesses - EXPECTED_HARNESSES
        if missing:
            errors.append(f"missing harnesses: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"unexpected harnesses: {', '.join(sorted(extra))}")
    for harness_path in sorted(HARNESSES.glob("*.yaml")):
        text = read_checked(harness_path, errors)
        require_keys(
            harness_path,
            text,
            {"id", "name", "purpose", "entrypoint", "autonomy_level", "human_gates", "stages", "completion_criteria"},
            errors,
        )
        if not re.search(rf"^id: {re.escape(harness_path.stem)}$", text, re.M):
            errors.append(f"{harness_path.relative_to(ROOT)}: id mismatch")
        validate_references(harness_path, text, known_skills, EXPECTED_AGENTS, errors)

    known_pipelines = {path.name for path in PIPELINES.glob("*.md")}
    if known_pipelines != EXPECTED_PIPELINES:
        missing = EXPECTED_PIPELINES - known_pipelines
        extra = known_pipelines - EXPECTED_PIPELINES
        if missing:
            errors.append(f"missing pipelines: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"unexpected pipelines: {', '.join(sorted(extra))}")
    for pipeline_name in sorted(EXPECTED_PIPELINES):
        pipeline_path = PIPELINES / pipeline_name
        text = read_checked(pipeline_path, errors)
        if "## Gates" not in text:
            errors.append(f"{pipeline_path.relative_to(ROOT)}: missing Gates section")

    known_integrations = {path.name for path in INTEGRATIONS.iterdir() if path.is_dir()}
    if known_integrations != EXPECTED_INTEGRATIONS:
        missing = EXPECTED_INTEGRATIONS - known_integrations
        extra = known_integrations - EXPECTED_INTEGRATIONS
        if missing:
            errors.append(f"missing integrations: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"unexpected integrations: {', '.join(sorted(extra))}")
    for integration in sorted(EXPECTED_INTEGRATIONS):
        read_checked(INTEGRATIONS / integration / "README.md", errors)

    matrix = ROOT / "data" / "agent-runtime-matrix.csv"
    matrix_text = read_checked(matrix, errors)
    for agent in sorted(EXPECTED_AGENTS):
        if not re.search(rf"^{re.escape(agent)},", matrix_text, re.M):
            errors.append(f"{matrix.relative_to(ROOT)}: missing matrix row for {agent}")
    read_checked(ROOT / "docs" / "references" / "agent-runtime-matrix.md", errors)
    validate_example_files(known_skills, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: validated {count} skills, {len(EXPECTED_AGENTS)} agents, {len(EXPECTED_HARNESSES)} harnesses")
    return 0


if __name__ == "__main__":
    sys.exit(main())
