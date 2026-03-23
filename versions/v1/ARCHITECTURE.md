# v1 Architecture — Standalone FastAPI Backend

## Overview

v1 is a single-process, single-service FastAPI application. It follows a classic layered architecture: routes → endpoints → services → ORM → database. There are no microservices, no message queues (except optional Redis caching), and no separate frontend process.

---

## Directory Structure and Responsibilities

```
app/
├── main.py              # FastAPI app factory, middleware, router registration
├── api/
│   ├── deps.py          # Dependency injection (get_db, get_current_user)
│   ├── crud.py          # Generic CRUD helpers
│   └── v1/
│       ├── router.py    # Aggregates all endpoint routers
│       └── endpoints/   # One file per domain module
├── core/
│   ├── config.py        # Pydantic Settings — all env vars
│   └── security.py      # JWT creation/validation, password hashing
├── db/
│   ├── base.py          # SQLAlchemy declarative base
│   ├── session.py       # Engine + SessionLocal factory
│   └── registry.py      # Model registry for Alembic
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic layer
└── reports/             # PDF and Excel generation
```

---

## Request Lifecycle

```
HTTP Request
    │
    ▼
main.py — CORS middleware, exception handlers
    │
    ▼
api/v1/router.py — routes to correct endpoint module
    │
    ▼
endpoints/*.py — validates input (Pydantic), checks auth (Depends)
    │
    ├── deps.py: get_db() → yields SQLAlchemy Session
    └── deps.py: get_current_user() → decodes JWT, returns User
    │
    ▼
services/*.py — business logic, external API calls
    │
    ▼
models/*.py — SQLAlchemy ORM queries
    │
    ▼
PostgreSQL
```

---

## Authentication Flow

```
POST /api/v1/auth/login
  ├── Look up user by username in DB
  ├── Verify password with bcrypt (passlib)
  ├── Create JWT: {"sub": user.id, "role": user.role, "exp": now+30min}
  └── Return {"access_token": "...", "token_type": "bearer"}

Protected endpoint:
  ├── Extract token from Authorization header
  ├── Decode with SECRET_KEY (HS256)
  ├── Load user from DB by sub claim
  └── Inject as current_user into endpoint function
```

---

## Database Layer

- SQLAlchemy 2.0 with declarative models
- All models inherit from `app.db.base.Base`
- Alembic manages migrations — run `alembic upgrade head` to apply
- Session lifecycle: one session per request, closed after response via `yield` in `deps.get_db()`

### Model Relationships (core)

```
AcademicYear
    └── Term
         └── Course
              ├── Subject
              ├── Enrollment (Student ↔ Course)
              └── Timetable

Student
    ├── Enrollment
    ├── AttendanceRecord
    ├── ExamResult
    ├── FeeRecord
    └── HostelAllocation

Faculty
    ├── TeachingAssignment (Faculty ↔ Subject)
    └── AttendanceRecord
```

---

## External Integrations

| Integration | Module | Purpose |
|-------------|--------|---------|
| M-Pesa Daraja | `services/mpesa.py` | Fee payments via mobile money |
| Africa's Talking | `services/sms.py` | SMS notifications |
| NEMIS | `endpoints/nemis.py` | Kenya national student registry |
| KNEC | `endpoints/knec.py` | Kenya national exam results |
| TPAD | `endpoints/tpad.py` | Teacher performance appraisal |
| Redis | `core/cache.py` | Analytics and dashboard caching |

---

## Caching Strategy

Redis is used for expensive read operations:
- Dashboard summary stats (TTL: 5 minutes)
- Analytics aggregations (TTL: 15 minutes)
- NEMIS/KNEC data (TTL: 1 hour)

Cache keys follow the pattern: `openemis:v1:{resource}:{params_hash}`

---

## Report Generation

`app/reports/` contains generators for:
- PDF reports (ReportLab or WeasyPrint)
- Excel exports (openpyxl)

Reports are generated on-demand and streamed as file downloads. For large reports, consider moving generation to a background task.

---

## Mobile App Integration

The Flutter app in `mobile/` connects to this API. Key considerations:
- All endpoints return JSON — no HTML
- JWT tokens are stored in Flutter's secure storage
- The mobile app uses the same `/api/v1/` base path
- Student portal endpoints (`/student-portal/`) are the primary mobile interface

---

## Configuration Reference

All configuration is in `app/core/config.py` via Pydantic Settings. Values are loaded from environment variables or `.env` file.

| Setting | Default | Description |
|---------|---------|-------------|
| `APP_NAME` | `CBC EMIS Kenya` | Application name |
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection |
| `SECRET_KEY` | (must set) | JWT signing key |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token lifetime |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `MPESA_BASE_URL` | sandbox URL | M-Pesa environment |

---

## Scaling Considerations

- Run multiple Gunicorn workers: `-w 4` for a 2-core server
- Use `uvicorn.workers.UvicornWorker` for async support
- Redis caching reduces DB load for read-heavy analytics
- For very high load, consider splitting the Kenya-specific integrations (NEMIS, KNEC, M-Pesa) into separate microservices
