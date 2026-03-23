# app/api — REST API Layer (v2)

Versioned FastAPI route definitions for the v2 full-stack EMIS backend.

## Structure

- `deps.py` — Shared dependencies: DB session injection, JWT-based current user extraction, role guards.
- `v2/` — All route modules under the `/api/v2` prefix, grouped by domain.

## Route Modules (v2/)

| Module | Endpoints |
|---|---|
| `auth.py` | Login, refresh token, logout |
| `students.py` | Student CRUD, enrollment, profile management |
| `faculty.py` | Teacher and department management |
| `admissions.py` | Application submission, review, status updates |
| `attendance.py` | Mark attendance, fetch summaries, export |
| `exams.py` | Exam sessions, result entry, grade reports |
| `fees.py` | Fee structures, invoices, M-Pesa STK push |
| `timetable.py` | Class schedules, period management |
| `library.py` | Book catalogue, issue/return tracking |
| `cbc.py` | CBC strands, formative assessments, portfolios |
| `reports.py` | PDF/Excel report downloads |

## Improvements over v1

- Cleaner dependency injection patterns
- Improved pagination and filtering on list endpoints
- Better error handling with structured error responses
- WebSocket support for real-time notifications
