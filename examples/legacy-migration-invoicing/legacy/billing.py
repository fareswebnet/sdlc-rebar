"""The 'real legacy' invoicing module. It is the oracle: never edit it during the migration."""

from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
VAT = {"FR": Decimal("0.20"), "DE": Decimal("0.19")}


def _cents(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def compute_invoice(lines, customer_type, country):
    subtotal = sum((Decimal(str(q)) * Decimal(str(p)) for q, p in lines), Decimal(0))
    discount = Decimal(0)
    if customer_type == "pro" and subtotal > 1000:
        discount = _cents(subtotal * Decimal("0.05"))
    net = subtotal - discount
    vat = _cents(net * VAT.get(country, Decimal(0)))
    return {"subtotal": _cents(subtotal), "discount": discount, "vat": vat, "total": _cents(net) + vat}


def late_fee(amount, days_late):
    if days_late <= 30:
        return Decimal(0)
    periods = -(-(days_late - 30) // 30)
    amount = Decimal(str(amount))
    fee = amount * Decimal("0.015") * periods
    return _cents(min(fee, amount * Decimal("0.10")))
