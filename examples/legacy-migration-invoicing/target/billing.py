"""Migrated invoicing module. Behavior must match the legacy oracle; invalid input is rejected."""

from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
VAT_RATES = {"FR": Decimal("0.20"), "DE": Decimal("0.19")}
PRO_DISCOUNT_THRESHOLD = Decimal("1000")
PRO_DISCOUNT_RATE = Decimal("0.05")
LATE_FEE_RATE = Decimal("0.015")
LATE_FEE_CAP = Decimal("0.10")
GRACE_DAYS = 30


def _round(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def compute_invoice(lines, customer_type, country):
    """Legacy accepted negative quantities and produced negative invoices; the target rejects them (improvement)."""
    for quantity, price in lines:
        if Decimal(str(quantity)) <= 0 or Decimal(str(price)) < 0:
            raise ValueError("quantity must be positive and price must not be negative")
    subtotal = Decimal(0)
    for quantity, price in lines:
        subtotal += Decimal(str(quantity)) * Decimal(str(price))
    discount = _round(subtotal * PRO_DISCOUNT_RATE) if customer_type == "pro" and subtotal > PRO_DISCOUNT_THRESHOLD else Decimal(0)
    net = subtotal - discount
    vat = _round(net * VAT_RATES.get(country, Decimal(0)))
    return {"subtotal": _round(subtotal), "discount": discount, "vat": vat, "total": _round(net) + vat}


def late_fee(amount, days_late):
    if days_late <= GRACE_DAYS:
        return Decimal(0)
    started_periods = (days_late - GRACE_DAYS + GRACE_DAYS - 1) // GRACE_DAYS
    amount = Decimal(str(amount))
    return _round(min(amount * LATE_FEE_RATE * started_periods, amount * LATE_FEE_CAP))


def _internal_helper():
    return None
