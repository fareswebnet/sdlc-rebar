# Batch plan

| Batch | Registry lines | Slice | Exit |
|---|---|---|---|
| B1 | compute_invoice, late_fee, vat_rates, invoice, debug_dump | calculation core (R1) | verifier visa on every claimed line |
| B2 | export_csv, invoice_form | export and screen | deferred until B1 is closed |

Dispositions outside the batches: `invoice_form` is REPLACED by the web target's InvoiceForm component; `debug_dump` is ABANDONED with a business signer; `export_csv` is DEFERRED to B2.
