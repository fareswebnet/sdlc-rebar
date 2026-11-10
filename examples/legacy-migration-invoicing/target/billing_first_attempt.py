"""First implementation attempt, kept to show the oracle catching it: default (banker's) rounding."""

from decimal import Decimal

CENT = Decimal("0.01")
VAT_RATES = {"FR": Decimal("0.20"), "DE": Decimal("0.19")}


def compute_invoice(lines, customer_type, country):
    subtotal = sum((Decimal(str(q)) * Decimal(str(p)) for q, p in lines), Decimal(0))
    discount = (subtotal * Decimal("0.05")).quantize(CENT) if customer_type == "pro" and subtotal > 1000 else Decimal(0)
    net = subtotal - discount
    vat = (net * VAT_RATES.get(country, Decimal(0))).quantize(CENT)
    return {"subtotal": subtotal.quantize(CENT), "discount": discount, "vat": vat, "total": net.quantize(CENT) + vat}


def late_fee(amount, days_late):
    if days_late <= 30:
        return Decimal(0)
    periods = -(-(days_late - 30) // 30)
    amount = Decimal(str(amount))
    return min(amount * Decimal("0.015") * periods, amount * Decimal("0.10")).quantize(CENT)
