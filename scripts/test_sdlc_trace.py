#!/usr/bin/env python3
"""Self-test for sdlc_trace.py using a temporary repo."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sdlc_trace  # noqa: E402


def build(root: Path, tasks: str, feature: str, tests: str) -> None:
    (root / "docs/product/bdd").mkdir(parents=True)
    (root / "docs/engineering").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "docs/product/prd.md").write_text("# PRD\n- FR-001 User can export a report\n- FR-002 Export is audited\n")
    (root / "docs/product/bdd/export.feature").write_text(feature)
    (root / "docs/engineering/tasks.md").write_text(tasks)
    (root / "tests/test_export.py").write_text(tests)


class TraceTests(unittest.TestCase):
    def run_case(self, tasks, feature, tests):
        with tempfile.TemporaryDirectory() as tmp:
            build(Path(tmp), tasks, feature, tests)
            return sdlc_trace.analyze(sdlc_trace.collect(Path(tmp)))

    def test_fully_traced(self):
        result = self.run_case(
            "- [x] T001 (FR-001) Export in src/export.py\n- [x] T002 (FR-002) Audit in src/audit.py\n",
            "@FR-001\nScenario: export\n@FR-002\nScenario: audit\n",
            "# FR-001 FR-002\n",
        )
        self.assertEqual(result["metrics"]["high"], 0)
        self.assertEqual(result["metrics"]["coverage_percent"], 100.0)

    def test_gaps_detected(self):
        result = self.run_case(
            "- [x] T001 (FR-001) Export\n- [ ] Missing id\n- [ ] T001 (FR-009) Duplicate and unknown\n",
            "@FR-001\nScenario: export\n",
            "no ids here\n",
        )
        messages = " | ".join(f["message"] for f in result["findings"])
        self.assertIn("no BDD scenario", messages)
        self.assertIn("no task implements", messages)
        self.assertIn("unknown requirement FR-009", messages)
        self.assertIn("duplicate task id T001", messages)
        self.assertIn("without T### id", messages)
        self.assertIn("no test mentions FR-001", messages)


if __name__ == "__main__":
    unittest.main()
