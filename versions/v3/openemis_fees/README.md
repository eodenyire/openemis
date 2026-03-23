# openemis_fees — Fees & Finance Module

Manages fee structures, student invoicing, and payment tracking.

## Models
- `op.fees.master` — Fee master templates per course/batch
- `op.fees.terms` — Fee payment terms and schedules
- `op.fees.line` — Individual fee line items
- `op.student.fees.details` — Student fee invoices
- `op.student.fees.payment` — Payment records

## Key Features
- Configurable fee structures per course and batch
- Automatic invoice generation
- Payment recording and receipt printing
- Outstanding fees reports
- Fee waiver and scholarship support
- Integration with Odoo accounting

## Depends On
`openemis_core`, `account`
