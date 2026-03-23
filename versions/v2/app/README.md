# app — FastAPI Backend Package (v2)

The FastAPI backend for openEMIS v2. Re-engineered from the openeducat Odoo modules into a standalone Python service with a richer domain model than v1.

## Structure

```
app/
├── api/v2/endpoints/   # Route handlers
├── core/               # Config and security
├── db/                 # Database session, base, registry
├── models/             # SQLAlchemy ORM models
└── schemas/            # Pydantic schemas
```

## Sub-packages

### `api/v2/endpoints/`
REST API route handlers organized by domain:

| File | Domain |
|------|--------|
| `auth.py` | JWT authentication |
| `core.py` | Students, faculty, courses, departments |
| `admission.py` | Admissions workflow |
| `attendance.py` | Attendance tracking |
| `exam.py` | Examinations and results |
| `fees.py` | Fee structures and payments |
| `library.py` | Library management |
| `timetable.py` | Class timetables |
| `transport.py` | Transportation |
| `hostel.py` | Hostel management |
| `lms.py` | Learning management |
| `digiguide.py` | Career guidance |
| `mentorship.py` | Mentorship platform |
| `alumni.py` | Alumni management |
| `events.py` | Events management |
| `facilities.py` | Facilities management |
| `health.py` | Health records |
| `noticeboard.py` | Notice board |
| `scholarships.py` | Scholarships |

### `core/`
- `config.py` — Pydantic Settings. App name `openEMIS v2`, version `2.0.0`. Configures DB URL, JWT, CORS origins (`localhost:3000`, `localhost:3001`, `localhost:8001`).
- `security.py` — JWT token creation and password hashing.

### `db/`
- `session.py` — SQLAlchemy engine and session factory.
- `base.py` — Declarative base.
- `registry.py` — Imports all models to register them before `create_all`.

### `models/`
SQLAlchemy models reverse-engineered from openeducat Odoo modules:

| File | Models |
|------|--------|
| `user.py` | User accounts and authentication |
| `core.py` | Student, faculty, department, program, course, batch, subject, academic year/term |
| `admission.py` | Admission register, applications |
| `attendance.py` | Class attendance, faculty attendance |
| `exam.py` | Exam sessions, mark sheets, results, grade config |
| `fees.py` | Fee master, fee lines, invoices, payments |
| `lms.py` | LMS courses, content, enrollments, quizzes |
| `timetable.py` | Timetable slots, room allocation |
| `cbc.py` | CBC strands, learning outcomes, assessments |
| `digiguide.py` | Career profiles, KUCCPS data, predictions |
| `facilities.py` | Rooms, labs, equipment |
| `health.py` | Student health records, visits |
| `support.py` | Support tickets, helpdesk |
| `extras.py` | Achievements, activities, alumni, events, scholarships |

### `schemas/`
Pydantic v2 schemas for all API request/response models, mirroring the models structure.
