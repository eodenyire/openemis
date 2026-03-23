# app/schemas — Pydantic Schemas (v2)

Request/response validation schemas for all v2 API endpoints.

## Purpose

Schemas enforce the API contract independently of the database layer. Every endpoint uses a schema for input validation and a separate schema for response serialisation.

## Schema Files

| File | Schemas |
|---|---|
| `user.py` | `UserCreate`, `UserRead`, `TokenPair`, `RefreshRequest` |
| `student.py` | `StudentCreate`, `StudentRead`, `EnrollmentCreate` |
| `faculty.py` | `TeacherCreate`, `TeacherRead`, `DepartmentRead` |
| `admission.py` | `ApplicationCreate`, `ApplicationRead`, `StatusUpdate` |
| `attendance.py` | `AttendanceMarkRequest`, `AttendanceSummary` |
| `exam.py` | `ResultEntry`, `GradeReportRead`, `ResultSlipRead` |
| `fees.py` | `InvoiceCreate`, `PaymentCreate`, `MpesaCallbackPayload` |
| `cbc.py` | `AssessmentCreate`, `PortfolioRead`, `StrandRead` |
| `core.py` | `SchoolRead`, `AcademicYearRead`, `TermRead` |

## Pattern

- `Base` — shared fields
- `Create` — input schema (no `id`, no timestamps)
- `Read` — full response with `id`, timestamps, and nested objects
- `Update` — partial update schema with all fields optional
