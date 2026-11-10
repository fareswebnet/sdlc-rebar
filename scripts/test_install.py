#!/usr/bin/env python3
"""Self-test for install.py and skill_index.py."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
INSTALL = str(SCRIPTS / "install.py")
INDEX = str(SCRIPTS / "skill_index.py")


def run(*args):
    return subprocess.run([sys.executable, *args], capture_output=True, text=True)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.target = self.root / "app"
        self.home = self.root / "home"
        self.target.mkdir()

    def install(self, *extra):
        return run(INSTALL, "--target", str(self.target), "--home", str(self.home), *extra)

    def test_project_paths_per_runtime(self):
        expected = {"claude": ".claude/skills", "codex": ".agents/skills", "antigravity": ".agents/skills", "generic": ".agents/skills"}
        for runtime, rel in expected.items():
            target = self.root / runtime
            target.mkdir()
            result = run(INSTALL, "--runtime", runtime, "--target", str(target), "--home", str(self.home))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / rel / "sdlc-task-breakdown" / "SKILL.md").exists(), runtime)

    def test_user_scope_paths(self):
        self.assertEqual(self.install("--runtime", "codex", "--scope", "user").returncode, 0)
        self.assertTrue((self.home / ".codex/skills/sdlc-task-breakdown/SKILL.md").exists())
        self.assertEqual(self.install("--runtime", "antigravity", "--scope", "user").returncode, 0)
        self.assertTrue((self.home / ".gemini/config/skills/sdlc-task-breakdown/SKILL.md").exists())
        self.assertNotEqual(self.install("--runtime", "generic", "--scope", "user").returncode, 0)

    def test_agents_md_is_managed_and_idempotent(self):
        agents = self.target / "AGENTS.md"
        agents.write_text("# My project\n\nKeep this text.\n")
        self.install("--runtime", "claude", "--agents-md", "--roles", "--with-kit")
        first = agents.read_text()
        self.assertIn("Keep this text.", first)
        self.assertIn("kit location: `.sdlc`", first)
        self.assertIn("(`orchestrator`)", first)
        self.assertTrue((self.target / ".sdlc/scripts/sdlc_registry.py").exists())
        self.install("--runtime", "claude", "--agents-md", "--roles", "--with-kit")
        self.assertEqual(first, agents.read_text())
        self.assertFalse((self.target / "CLAUDE.md").exists())
        self.assertFalse((self.target / "GEMINI.md").exists())

    def test_existing_skills_kept_without_force_and_dry_run_writes_nothing(self):
        dry = self.install("--runtime", "codex", "--dry-run", "--agents-md")
        self.assertEqual(dry.returncode, 0)
        self.assertFalse((self.target / ".agents").exists())
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.install("--runtime", "codex")
        marker = self.target / ".agents/skills/sdlc-task-breakdown/local-note.txt"
        marker.write_text("keep")
        self.install("--runtime", "codex")
        self.assertTrue(marker.exists())
        self.install("--runtime", "codex", "--force")
        self.assertFalse(marker.exists())

    def test_native_roles_claude_only(self):
        self.assertEqual(self.install("--runtime", "claude", "--native-roles").returncode, 0)
        text = (self.target / ".claude/agents/independent-verifier.md").read_text()
        self.assertIn("name: independent-verifier", text)
        self.assertNotEqual(self.install("--runtime", "codex", "--native-roles").returncode, 0)

    def test_link_mode(self):
        self.install("--runtime", "generic", "--mode", "link")
        self.assertTrue((self.target / ".agents/skills/sdlc-task-breakdown").is_symlink())

    def test_skill_index(self):
        out = run(INDEX, "--select", "migrate legacy system registry", "--top", "3").stdout
        self.assertIn("sdlc-legacy-inventory-registry", out)
        self.assertIn("# SDLC Task Breakdown", run(INDEX, "--skill", "sdlc-task-breakdown").stdout)


if __name__ == "__main__":
    unittest.main()
