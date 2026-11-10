#!/usr/bin/env python3
"""Frozen-registry tool for migrations and system merges.

The registry is the denominator of every progress claim: one CSV line per thing that existed
(action, route, screen, entity, table, command, server call, business rule). Commands:

  init     create or merge a registry from an inventory CSV (never loses a decision, never deletes a line)
  check    enforce disposition rules (exit 1 on violation)
  report   progress against the full denominator, by disposition and by batch
  sample   reproducible audit sample for a batch (all priority-1 lines plus a random share of the rest)
  claim    implementer moves lines OPEN -> TO_VERIFY with proof (cannot set PORTED)
  visa     independent verifier moves lines TO_VERIFY -> PORTED, or refuses back to OPEN
  ratchet  fail on new violations; fail when the baseline contains violations that are now resolved

Dispositions: OPEN, TO_VERIFY, PORTED, REPLACED, ABANDONED, DEFERRED.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import random
import sys
from pathlib import Path

HEADER = ["key", "source", "kind", "name", "note", "disposition", "proof_type", "proof_ref", "batch", "priority",
          "justification", "signer", "implementer", "verifier_visa", "visa_date"]
DISPOSITIONS = {"OPEN", "TO_VERIFY", "PORTED", "REPLACED", "ABANDONED", "DEFERRED"}


def load(path: Path) -> tuple[list[dict], str]:
    raw = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.DictReader(io.StringIO(raw, newline="")))
    return rows, newline


def save(path: Path, rows: list[dict], newline: str) -> None:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, HEADER, lineterminator=newline, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in HEADER})
    path.write_bytes(out.getvalue().encode("utf-8"))


def violations(rows: list[dict]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for row in rows:
        key = row.get("key", "")
        if not key:
            found.append("line without key")
            continue
        if key in seen:
            found.append(f"{key}: duplicate key")
        seen.add(key)
        disposition = row.get("disposition", "")
        if disposition not in DISPOSITIONS:
            found.append(f"{key}: invalid disposition {disposition!r}")
            continue
        if disposition == "TO_VERIFY" and not row.get("proof_ref"):
            found.append(f"{key}: TO_VERIFY needs proof_ref")
        if disposition == "PORTED":
            for field in ("proof_type", "proof_ref", "verifier_visa", "visa_date"):
                if not row.get(field):
                    found.append(f"{key}: PORTED needs {field}")
            if row.get("verifier_visa") and row.get("verifier_visa") == row.get("implementer"):
                found.append(f"{key}: verifier must differ from implementer")
        if disposition == "REPLACED" and not row.get("justification"):
            found.append(f"{key}: REPLACED must name the replacement in justification")
        if disposition == "ABANDONED" and not (row.get("justification") and row.get("signer")):
            found.append(f"{key}: ABANDONED needs justification and business signer")
        if disposition == "DEFERRED" and not row.get("batch"):
            found.append(f"{key}: DEFERRED needs a named batch")
    return found


def cmd_init(args) -> int:
    inventory = list(csv.DictReader(open(args.inventory, newline="", encoding="utf-8")))
    path = Path(args.registry)
    rows, newline = (load(path) if path.exists() else ([], "\n"))
    index = {r["key"]: r for r in rows}
    added = 0
    current = set()
    for item in inventory:
        key = item["key"]
        current.add(key)
        if key in index:
            continue
        row = {k: item.get(k, "") for k in HEADER}
        row["disposition"] = item.get("disposition") or "OPEN"
        rows.append(row)
        index[key] = row
        added += 1
    marked = 0
    for row in rows:
        if row["key"] not in current and "DISAPPEARED_FROM_INVENTORY" not in row.get("note", ""):
            row["note"] = (row.get("note", "") + " DISAPPEARED_FROM_INVENTORY").strip()
            marked += 1
    save(path, rows, newline)
    print(f"registry {path}: {len(rows)} lines, {added} added, {marked} marked as disappeared (never deleted)")
    return 0


def cmd_check(args) -> int:
    rows, _ = load(Path(args.registry))
    found = violations(rows)
    for item in found:
        print(f"VIOLATION: {item}")
    print(f"{len(rows)} lines, {len(found)} violations")
    return 1 if found else 0


def cmd_report(args) -> int:
    rows, _ = load(Path(args.registry))
    total = len(rows)
    by_disp: dict[str, int] = {}
    by_batch: dict[str, dict[str, int]] = {}
    for row in rows:
        by_disp[row["disposition"]] = by_disp.get(row["disposition"], 0) + 1
        batch = row.get("batch") or "(no batch)"
        by_batch.setdefault(batch, {})
        by_batch[batch][row["disposition"]] = by_batch[batch].get(row["disposition"], 0) + 1
    closed = sum(by_disp.get(d, 0) for d in ("PORTED", "REPLACED", "ABANDONED"))
    print(f"denominator: {total}")
    for disposition in sorted(by_disp):
        print(f"  {disposition}: {by_disp[disposition]}")
    print(f"closed with proof or decision: {closed} ({100 * closed / total:.1f}%)" if total else "empty registry")
    for batch in sorted(by_batch):
        print(f"  batch {batch}: " + ", ".join(f"{d}={n}" for d, n in sorted(by_batch[batch].items())))
    unbatched = sum(1 for r in rows if not r.get("batch") and r["disposition"] in {"OPEN", "TO_VERIFY"})
    if unbatched:
        print(f"WARNING: {unbatched} open lines belong to no batch")
    return 0


def cmd_sample(args) -> int:
    rows, _ = load(Path(args.registry))
    pool = [r for r in rows if r.get("batch") == args.batch and r["disposition"] == "TO_VERIFY"]
    priority = [r for r in pool if r.get("priority") == "1"]
    rest = [r for r in pool if r.get("priority") != "1"]
    rng = random.Random(args.seed)
    count = min(len(rest), max(1, round(len(rest) * args.rate))) if rest else 0
    picked = priority + rng.sample(rest, count)
    print(f"batch {args.batch}: {len(pool)} to verify, sampled {len(picked)} (all {len(priority)} priority-1 + {count} random, seed {args.seed})")
    for row in picked:
        print(row["key"])
    return 0


def _apply(args, new_disposition: str, allowed_from: str) -> int:
    path = Path(args.registry)
    rows, newline = load(path)
    index = {r["key"]: r for r in rows}
    errors = []
    for key in args.keys:
        row = index.get(key)
        if row is None:
            errors.append(f"{key}: unknown key")
        elif row["disposition"] != allowed_from:
            errors.append(f"{key}: expected {allowed_from}, found {row['disposition']}")
    if new_disposition == "TO_VERIFY" and not args.proof_ref:
        errors.append("claim needs --proof-ref")
    if errors:
        for e in errors:
            print(f"REFUSED: {e}")
        return 1
    for key in args.keys:
        row = index[key]
        if new_disposition == "TO_VERIFY":
            row.update(disposition="TO_VERIFY", proof_ref=args.proof_ref, proof_type=args.proof_type, implementer=args.implementer)
        elif args.refuse:
            row.update(disposition="OPEN", note=(row.get("note", "") + f" REFUSED: {args.refuse}").strip())
        else:
            if args.verifier == row.get("implementer"):
                print(f"REFUSED: {key}: verifier must differ from implementer")
                return 1
            row.update(disposition="PORTED", verifier_visa=args.verifier, visa_date=dt.date.today().isoformat())
    save(path, rows, newline)
    print(f"{len(args.keys)} lines updated")
    return 0


def cmd_claim(args) -> int:
    return _apply(args, "TO_VERIFY", "OPEN")


def cmd_visa(args) -> int:
    if not args.refuse and not args.verifier:
        print("REFUSED: visa needs --verifier or --refuse")
        return 1
    return _apply(args, "PORTED", "TO_VERIFY")


def cmd_ratchet(args) -> int:
    baseline = {l.strip() for l in Path(args.baseline).read_text().splitlines() if l.strip()}
    current = {l.strip() for l in Path(args.current).read_text().splitlines() if l.strip()}
    new, resolved = sorted(current - baseline), sorted(baseline - current)
    for item in new:
        print(f"NEW VIOLATION: {item}")
    for item in resolved:
        print(f"RESOLVED, remove from baseline: {item}")
    print(f"baseline {len(baseline)}, current {len(current)}, new {len(new)}, resolved {len(resolved)}")
    return 1 if new or resolved else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("registry"); p.add_argument("inventory"); p.set_defaults(fn=cmd_init)
    p = sub.add_parser("check"); p.add_argument("registry"); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("report"); p.add_argument("registry"); p.set_defaults(fn=cmd_report)
    p = sub.add_parser("sample"); p.add_argument("registry"); p.add_argument("--batch", required=True)
    p.add_argument("--rate", type=float, default=0.1); p.add_argument("--seed", type=int, required=True); p.set_defaults(fn=cmd_sample)
    p = sub.add_parser("claim"); p.add_argument("registry"); p.add_argument("keys", nargs="+")
    p.add_argument("--proof-ref"); p.add_argument("--proof-type", default="HTTP_LIVE"); p.add_argument("--implementer", required=True); p.set_defaults(fn=cmd_claim)
    p = sub.add_parser("visa"); p.add_argument("registry"); p.add_argument("keys", nargs="+")
    p.add_argument("--verifier"); p.add_argument("--refuse", help="reason; sends lines back to OPEN"); p.set_defaults(fn=cmd_visa)
    p = sub.add_parser("ratchet"); p.add_argument("baseline"); p.add_argument("current"); p.set_defaults(fn=cmd_ratchet)
    args = parser.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
