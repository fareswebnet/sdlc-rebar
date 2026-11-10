#!/usr/bin/env python3
"""Self-test for sdlc_registry.py."""

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = str(Path(__file__).resolve().parent / "sdlc_registry.py")


def run(*args):
    return subprocess.run([sys.executable, TOOL, *args], capture_output=True, text=True)


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.inv = self.dir / "inv.csv"
        rows = [("a#1", "ACTION", "1", "B1"), ("a#2", "ACTION", "1", "B1"), ("a#3", "SCREEN", "2", "B1"), ("a#4", "TABLE", "2", "B1")]
        with open(self.inv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["key", "kind", "priority", "batch"])
            w.writerows(rows)
        self.reg = self.dir / "registry.csv"
        self.assertEqual(run("init", str(self.reg), str(self.inv)).returncode, 0)

    def test_full_lifecycle_and_independence(self):
        self.assertEqual(run("check", str(self.reg)).returncode, 0)
        self.assertEqual(run("claim", str(self.reg), "a#1", "--proof-ref", "tests/t.py::x", "--implementer", "agentA").returncode, 0)
        self.assertEqual(run("visa", str(self.reg), "a#1", "--verifier", "agentA").returncode, 1)  # self-approval refused
        self.assertEqual(run("visa", str(self.reg), "a#1", "--verifier", "agentB").returncode, 0)
        self.assertEqual(run("check", str(self.reg)).returncode, 0)
        report = run("report", str(self.reg)).stdout
        self.assertIn("denominator: 4", report)
        self.assertIn("PORTED: 1", report)

    def test_visa_requires_claim_and_refuse_reopens(self):
        self.assertEqual(run("visa", str(self.reg), "a#2", "--verifier", "agentB").returncode, 1)
        run("claim", str(self.reg), "a#2", "--proof-ref", "p", "--implementer", "agentA")
        self.assertEqual(run("visa", str(self.reg), "a#2", "--refuse", "field ignored").returncode, 0)
        text = self.reg.read_text()
        self.assertIn("REFUSED: field ignored", text)

    def test_check_catches_abandoned_without_signer_and_never_deletes(self):
        rows = list(csv.DictReader(open(self.reg, newline="")))
        rows[2]["disposition"] = "ABANDONED"
        rows[2]["justification"] = "obsolete"
        with open(self.reg, "w", newline="") as fh:
            w = csv.DictWriter(fh, list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        self.assertEqual(run("check", str(self.reg)).returncode, 1)
        with open(self.inv, "w", newline="") as fh:
            csv.writer(fh).writerows([["key", "kind", "priority", "batch"], ["a#1", "ACTION", "1", "B1"]])
        run("init", str(self.reg), str(self.inv))
        self.assertEqual(len(list(csv.DictReader(open(self.reg, newline="")))), 4)
        self.assertIn("DISAPPEARED_FROM_INVENTORY", self.reg.read_text())

    def test_sample_is_reproducible_and_includes_priority_one(self):
        for k in ("a#1", "a#2", "a#3", "a#4"):
            run("claim", str(self.reg), k, "--proof-ref", "p", "--implementer", "agentA")
        a = run("sample", str(self.reg), "--batch", "B1", "--rate", "0.5", "--seed", "7").stdout
        b = run("sample", str(self.reg), "--batch", "B1", "--rate", "0.5", "--seed", "7").stdout
        self.assertEqual(a, b)
        self.assertIn("a#1", a)
        self.assertIn("a#2", a)

    def test_ratchet(self):
        base, cur = self.dir / "b.txt", self.dir / "c.txt"
        base.write_text("x\ny\n"); cur.write_text("x\ny\n")
        self.assertEqual(run("ratchet", str(base), str(cur)).returncode, 0)
        cur.write_text("x\nz\n")
        out = run("ratchet", str(base), str(cur))
        self.assertEqual(out.returncode, 1)
        self.assertIn("NEW VIOLATION: z", out.stdout)
        self.assertIn("RESOLVED, remove from baseline: y", out.stdout)


if __name__ == "__main__":
    unittest.main()
