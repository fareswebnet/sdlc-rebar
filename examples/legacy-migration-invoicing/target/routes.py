"""Public routes of the migrated service. Every public function of billing.py must appear here."""

from . import billing

ROUTES = {
    "POST /invoices/compute": billing.compute_invoice,
    "POST /invoices/late-fee": billing.late_fee,
}
