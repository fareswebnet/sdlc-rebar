# Business rules: legacy-billing

Status: observed = read from code; confirmed = approved by the business owner. Risk: R1 money.

| Id | Rule | Risk | Status | Registry key |
|---|---|---|---|---|
| RG-INV-001 | Customers of type `pro` with a subtotal strictly above 1000 get a 5% discount, rounded half up to the cent | R1 | confirmed | billing:compute_invoice |
| RG-INV-002 | VAT is 20% for FR, 19% for DE, 0 elsewhere, computed on the net amount and rounded half up | R1 | confirmed | billing:vat_rates |
| RG-INV-003 | Total is the rounded net amount plus VAT | R1 | confirmed | billing:invoice |
| RG-INV-004 | No late fee within 30 days; then 1.5% of the amount per started 30-day period, capped at 10% | R1 | confirmed | billing:late_fee |

## Legacy defects

| Id | Behavior | Decision |
|---|---|---|
| LEGACY_DEFECT-001 | Negative quantities are accepted and yield a negative invoice | Improve: reject with a validation error in the target |

## Open questions

None blocking.
