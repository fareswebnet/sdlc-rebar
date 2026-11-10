#!/usr/bin/env python3
"""Run the whole migration workflow end to end on the invoicing example.

Usage: python run_example.py [--write]   (--write refreshes artifacts/)
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parents[1] / "scripts" / "sdlc_registry.py"
sys.path.insert(0, str(HERE / "tests"))
import characterization as c  # noqa: E402


def registry(*args, expect=0):
    result = subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True)
    assert result.returncode == expect, f"{args} exited {result.returncode}: {result.stdout}{result.stderr}"
    return result.stdout


def detect_unrouted(target_dir: Path) -> list[str]:
    import re
    public = set(re.findall(r"^def ([a-z]\w*)\(", (target_dir / "billing.py").read_text(), re.M))
    routed = set(re.findall(r"billing\.(\w+)", (target_dir / "routes.py").read_text()))
    return sorted(f"unrouted public function {name}" for name in public - routed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    work = Path(tempfile.mkdtemp())
    reg = work / "registry.csv"
    log: list[str] = []

    def step(text):
        log.append(text)
        print(text)

    registry("init", str(reg), str(HERE / "inventory.csv"))
    registry("check", str(reg))
    step("1. Registry frozen: " + registry("report", str(reg)).splitlines()[0])

    first = c.diff(HERE / "target" / "billing_first_attempt.py")
    assert first, "oracle must catch the first attempt"
    step(f"2. Oracle caught the first attempt: {len(first)} mismatches, for example {first[0]}")

    final = c.diff(HERE / "target" / "billing.py")
    assert not final, final[:3]
    step("3. Final target matches the legacy oracle on boundaries and 2000 seeded fuzz cases per function (exact equality)")

    # Dispositions decided by people
    rows_text = reg.read_text()
    import csv, io
    rows = list(csv.DictReader(io.StringIO(rows_text, newline="")))
    for row in rows:
        if row["key"] == "web:invoice_form":
            row.update(disposition="REPLACED", justification="Replaced by the InvoiceForm component in the web target")
        if row["key"] == "billing:debug_dump":
            row.update(disposition="ABANDONED", justification="Developer-only dump, no business use", signer="J. Martin (Finance owner)")
        if row["key"] == "billing:export_csv":
            row.update(disposition="DEFERRED")
    with open(reg, "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    registry("check", str(reg))
    step("4. Business decisions recorded: 1 REPLACED, 1 ABANDONED with signer, 1 DEFERRED to B2")

    proofs = {
        "billing:compute_invoice": "tests/test_characterization.py::test_compute_invoice_matches_legacy",
        "billing:late_fee": "tests/test_characterization.py::test_late_fee_matches_legacy",
        "billing:vat_rates": "tests/test_characterization.py::test_vat_reference_data",
        "billing:invoice": "tests/test_characterization.py::test_compute_invoice_matches_legacy",
    }
    for key, proof in proofs.items():
        registry("claim", str(reg), key, "--proof-ref", proof, "--proof-type", "DIFFERENTIAL", "--implementer", "builder-agent")
    step("5. Builder claimed 4 lines with proof (disposition TO_VERIFY)")

    registry("visa", str(reg), "billing:compute_invoice", "--verifier", "builder-agent", expect=1)
    step("6. Self-approval refused by the tool")

    sample = registry("sample", str(reg), "--batch", "B1", "--rate", "1.0", "--seed", "42")
    step("7. Verifier drew the sample before reading evidence: " + sample.splitlines()[0])

    baseline = work / "baseline.txt"; baseline.write_text("")
    current = work / "current.txt"; current.write_text("\n".join(detect_unrouted(HERE / "target")) + "\n")
    registry("ratchet", str(baseline), str(current))
    current.write_text("unrouted public function export_csv\n")
    registry("ratchet", str(baseline), str(current), expect=1)
    step("8. Reachability ratchet green on the target; a new unrouted function would fail it")

    mutated = work / "mutated"
    shutil.copytree(HERE / "target", mutated)
    source = (mutated / "billing.py").read_text()
    assert 'Decimal("0.05")' in source
    (mutated / "billing.py").write_text(source.replace('Decimal("0.05")', 'Decimal("0.06")'))
    killed = c.diff(mutated / "billing.py")
    assert killed, "mutation must make the suite fail"
    step(f"9. Mutation check: changing the discount rate 5% to 6% fails {len(killed)} comparisons, so the proof proves something")

    for key in proofs:
        registry("visa", str(reg), key, "--verifier", "verifier-agent")
    registry("check", str(reg))
    report = registry("report", str(reg))
    step("10. Verifier granted visas; final report:\n" + report)
    assert "PORTED: 4" in report and "closed with proof or decision: 6 (85.7%)" in report, report

    if args.write:
        shutil.copy(reg, HERE / "artifacts" / "registry.final.csv")
        (HERE / "artifacts" / "run-log.md").write_text("# Run log\n\nGenerated by `python run_example.py --write`.\n\n" + "\n\n".join(log) + "\n")
        print("artifacts written")
    suite = subprocess.run([sys.executable, str(HERE / "tests" / "test_characterization.py")], capture_output=True, text=True)
    assert suite.returncode == 0, suite.stderr
    print("unit tests: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
