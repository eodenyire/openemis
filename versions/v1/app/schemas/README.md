# app/schemas — Pydantic Schemas (v1)

Request and response validation schemas for all API endpoints, built with Pydantic v2.

## Purpose

Schemas decouple the API contract from the database models. They define:
- What fields are required on input (POST/PUT)
- What fields are returned in responses
- Field types, constraints, and validation rules

## Structure

Each domain has a schema file mirroring the models:

| File | Schemas |
|---|---|
| `user.py` | `UserCreate`, `UserRead`, `Token`, `TokenData` |
| `student.py` | `StudentCreate`, `StudentRead`, `StudentUpdate` |
| `faculty.py` | `TeacherCreate`, `TeacherRead` |
| `admission.py` | `ApplicationCreate`, `ApplicationRead` |
| `attendance.py` | `AttendanceCreate`, `AttendanceRead` |
| `exam.py` | `ExamResultCreate`, `ExamResultRead`, `GradeReport` |
| `fees.py` | `InvoiceCreate`, `PaymentCreate`, `MpesaCallback` |
| `cbc.py` | `CBCAssessmentCreate`, `PortfolioRead` |

## Pattern

Each domain typically has three schema variants:
- `Base` — shared fields
- `Create` — fields required on creation (no `id`)
- `Read` — full response including `id`, timestamps, and nested relations
