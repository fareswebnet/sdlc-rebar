import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import characterization as c  # noqa: E402

TARGET = c.ROOT / "target" / "billing.py"


class CharacterizationTests(unittest.TestCase):
    def test_compute_invoice_matches_legacy(self):  # RG-INV-001, RG-INV-002, RG-INV-003
        self.assertEqual([m for m in c.diff(TARGET) if m.startswith("compute_invoice")], [])

    def test_late_fee_matches_legacy(self):  # RG-INV-004
        self.assertEqual([m for m in c.diff(TARGET) if m.startswith("late_fee")], [])

    def test_vat_reference_data(self):  # RG-INV-002
        target = c.load(TARGET, "t")
        self.assertEqual(target.VAT_RATES, {"FR": Decimal("0.20"), "DE": Decimal("0.19")})

    def test_negative_quantity_is_rejected(self):  # LEGACY_DEFECT-001, deliberate improvement
        target = c.load(TARGET, "t2")
        with self.assertRaises(ValueError):
            target.compute_invoice([(-1, "10.00")], "retail", "FR")


if __name__ == "__main__":
    unittest.main()
