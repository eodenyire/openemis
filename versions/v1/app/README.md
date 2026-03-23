# app — FastAPI Application Package (v1)

The core application package for openEMIS v1. Organized into focused sub-packages following clean architecture principles.

## Structure

```
app/
├── api/        # HTTP route handlers (endpoints)
├── core/       # Configuration and security
├── db/         # Database session and model registry
├── models/     # SQLAlchemy ORM models
├── schemas/    # Pydantic request/response schemas
├── services/   # External service integrations
├── reports/    # PDF and Excel report generators
└── static/     # Served HTML files (login, dashboard)
```

## Sub-packages

### `api/v1/endpoints/`
All REST API route handlers. Each file maps to a domain:

| File | Domain |
|------|--------|
| `auth.py` | JWT login/logout |
| `students.py` | Student CRUD |
| `users.py` | User management |
| `admission.py` | Admissions workflow |
| `attendance.py` | Attendance tracking |
| `exam.py` | Examinations |
| `fees.py` | Fee management |
| `library.py` / `library_v2.py` | Library operations |
| `timetable.py` / `timetable_v2.py` | Timetable management |
| `transport.py` / `transport_v2.py` | Transportation |
| `hostel.py` / `hostel_v2.py` | Hostel management |
| `hr.py` | Human resources |
| `payroll.py` | Payroll processing |
| `finance.py` | Financial management |
| `payments.py` | M-Pesa & payment processing |
| `cbc.py` | CBC curriculum management |
| `digiguide.py` | Career guidance |
| `mentorship.py` | Mentorship platform |
| `blog.py` | Educational blog |
| `lms.py` | Learning management |
| `analytics.py` | Reporting & analytics |
| `dashboard.py` | Dashboard stats |
| `parent_portal.py` | Parent-facing portal |
| `student_portal.py` | Student-facing portal |
| `teacher_portal.py` | Teacher-facing portal |
| `sms.py` | SMS notifications |
| `nemis.py` | NEMIS integration |
| `knec.py` | KNEC integration |
| `tpad.py` | TPAD (teacher appraisal) |
| `government.py` | Government reporting |
| `reports.py` | Report generation |

### `core/`
- `config.py` — Pydantic Settings class loading from `.env`. Covers DB URL, JWT secret, M-Pesa keys, Africa's Talking SMS, Redis URL, CORS origins.
- `security.py` — Password hashing and JWT token creation/verification.

### `db/`
- `session.py` — SQLAlchemy engine and `SessionLocal` factory. Provides `get_db()` dependency.
- `base.py` — Declarative base class shared by all models.
- `registry.py` — Imports all models to ensure they are registered with SQLAlchemy metadata before `create_all`.

### `models/`
SQLAlchemy ORM models organized by domain:

| File | Models |
|------|--------|
| `user.py` | User, roles, permissions |
| `people.py` | Person base model |
| `student.py` | Student profile |
| `student_lifecycle.py` | Enrollment, graduation, transfers |
| `teacher.py` | Teacher/faculty profile |
| `core.py` | Department, program, course, batch |
| `subject.py` | Subject definitions |
| `academic_year.py` | Academic year |
| `academic_term.py` | Academic term/semester |
| `admission.py` | Admission applications |
| `attendance.py` | Attendance records |
| `exam.py` | Exams, marks, results |
| `assignment.py` | Assignments and submissions |
| `fees.py` | Fee structures, invoices, payments |
| `library.py` | Books, members, issues |
| `hostel.py` | Rooms, allocations |
| `transportation.py` | Routes, vehicles, allocations |
| `timetable.py` | Class schedules |
| `lms.py` | Courses, content, enrollments |
| `cbc.py` | CBC strands, performance |
| `health.py` | Health records |
| `hr.py` | Staff records, leave, appraisals |
| `mpesa.py` | M-Pesa transaction records |
| `partner.py` | Partner/contact records |
| `tenant.py` | Multi-tenancy support |
| `extras.py` | Miscellaneous models |
| `communications.py` | Messaging and notifications |

### `schemas/`
Pydantic v2 schemas for request validation and response serialization, mirroring the models structure: `admission.py`, `attendance.py`, `core.py`, `exam.py`, `fees.py`, `library.py`, `people.py`, `student.py`, `timetable.py`, `transportation.py`, `user.py`, `common.py`, `extras.py`, `hostel.py`, `assignment.py`.

### `services/`
External service integrations:
- `mpesa.py` — Safaricom M-Pesa Daraja API (STK push, C2B, B2C)
- `sms.py` — Africa's Talking SMS gateway

### `reports/`
PDF and Excel report generators using ReportLab and openpyxl:
- `students.py` — Student lists, profiles, bonafide certificates
- `academic.py` — Academic performance reports
- `finance.py` — Fee statements, financial summaries
- `staff.py` — Staff reports
- `result_slips.py` — Exam result slips
- `support_services.py` — Support service reports
- `trends.py` — Trend analysis reports
- `helpers.py` — Shared report utilities

### `static/`
Static HTML files served directly by FastAPI:
- `index.html` — Login page (served at `/`)
- `dashboard.html` — Main dashboard (served at `/dashboard`)
