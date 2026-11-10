"""Differential comparison of a target module against the legacy oracle (exact equality, no tolerance)."""

import importlib.util
import random
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOUNDARIES = [
    ([(1, "1000.10")], "pro", "FR"),    # discount 50.005 must round half up
    ([(1, "1000.00")], "pro", "FR"),    # threshold is strictly greater than 1000
    ([(3, "0.05")], "retail", "DE"),     # vat on 0.15 is 0.0285
    ([(1, "0.01")], "retail", "FR"),
    ([(2, "499.99")], "pro", "US"),
]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def invoice_cases(seed: int, count: int):
    rng = random.Random(seed)
    for _ in range(count):
        lines = [(rng.choice([1, 2, 3, 5, 10, "0.5", "2.5"]), f"{rng.randint(1, 120000) / 100:.2f}") for _ in range(rng.randint(1, 4))]
        yield lines, rng.choice(["pro", "retail"]), rng.choice(["FR", "DE", "US"])


def diff(target_path: Path, seed: int = 42, count: int = 2000) -> list[str]:
    legacy = load(ROOT / "legacy" / "billing.py", "legacy_billing")
    target = load(target_path, "target_billing")
    mismatches = []
    for lines, customer, country in list(BOUNDARIES) + list(invoice_cases(seed, count)):
        if legacy.compute_invoice(lines, customer, country) != target.compute_invoice(lines, customer, country):
            mismatches.append(f"compute_invoice{(lines, customer, country)}")
    rng = random.Random(seed)
    for _ in range(count):
        amount, days = f"{rng.randint(100, 500000) / 100:.2f}", rng.randint(0, 400)
        if legacy.late_fee(amount, days) != target.late_fee(amount, days):
            mismatches.append(f"late_fee({amount}, {days})")
    return mismatches
