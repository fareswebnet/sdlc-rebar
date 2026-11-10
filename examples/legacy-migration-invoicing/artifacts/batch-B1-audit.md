# Batch B1 audit

Verifier: verifier-agent (fresh context, different from builder-agent)
Sample: `python scripts/sdlc_registry.py sample registry.csv --batch B1 --rate 1.0 --seed 42` drawn before reading evidence.

| Line | Priority | Exercised through | Wrong-role and cross-tenant | Fields checked | Mutation | Verdict |
|---|---|---|---|---|---|---|
| billing:compute_invoice | 1 | differential suite against the real legacy | not applicable to the library; to be covered at the HTTP layer | lines, customer_type, country | discount 5% to 6% fails 817 comparisons | OK |
| billing:late_fee | 2 | differential suite | not applicable | amount, days_late | covered by cap and period boundaries in fuzz | OK |
| billing:vat_rates | 2 | reference-data test plus differential suite | not applicable | FR, DE, other | rate change fails suite | OK |
| billing:invoice | 2 | totals compared with legacy | not applicable | subtotal, discount, vat, total | rounding change fails suite | OK |

## Gate

- Refusals: 0 of 4. Reachability ratchet: green. Self-approval attempt: refused by the tool.
- Open limitation: the example is a library, so HTTP-level role and tenant checks are out of scope here; a real batch must run them through the public interface.
