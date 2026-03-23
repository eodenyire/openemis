# app/reports — Report Generation (v1)

PDF and Excel report generation for the v1 EMIS backend.

## Reports Produced

| Report | Format | Description |
|---|---|---|
| Student Result Slip | PDF | Per-student exam results with grades and remarks |
| Class Report Card | PDF | Full class performance summary |
| CBC Portfolio | PDF | Competency-based curriculum learner portfolio |
| Attendance Summary | PDF/Excel | Daily, weekly, monthly attendance by class |
| Fee Statement | PDF | Student fee balance, payments, and outstanding amounts |
| M-Pesa Reconciliation | Excel | Payment transactions matched against invoices |
| Admission Report | PDF | Application statistics and status breakdown |

## Libraries Used

- `reportlab` — PDF generation
- `openpyxl` — Excel workbook creation
- `jinja2` — HTML templates for styled PDF output

## Usage

Report endpoints are exposed under `/api/v1/reports/`. They return file downloads with appropriate `Content-Disposition` headers. Reports are generated on-demand; for large datasets, generation is offloaded to a background task via Redis/Celery.
