# app/services — Business Logic Layer (v1)

Service modules that encapsulate business logic, keeping route handlers thin and testable.

## Services

| File | Responsibility |
|---|---|
| `auth.py` | User authentication, JWT creation, password reset flow |
| `mpesa.py` | M-Pesa Daraja API integration — STK push, C2B callbacks, payment verification |
| `sms.py` | Africa's Talking SMS — send notifications to parents/students |
| `email.py` | Email notifications for admissions, results, fee reminders |
| `cbc.py` | CBC assessment logic — strand scoring, portfolio generation, report card computation |
| `fees.py` | Fee invoice generation, payment reconciliation, balance calculation |
| `reports.py` | PDF/Excel report generation for results, attendance, fee statements |

## Design

Services are plain Python classes/functions imported by route handlers. They receive a database session and validated schema data, perform business operations, and return results. This keeps FastAPI route code to a minimum and makes unit testing straightforward.
