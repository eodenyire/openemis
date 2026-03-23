# openEMIS — System Architecture

## Overview

openEMIS is an Educational Management Information System that has evolved through four distinct architectural generations. Each version represents a different technology philosophy — from a lightweight REST API to a full enterprise ERP. All four versions share the same domain model (students, courses, exams, fees, attendance, HR) but differ in how they implement, expose, and present that domain.

---

## Version Lineage

```
v1 (FastAPI standalone)
  └─► v2 (FastAPI + Next.js frontend)
        └─► v3 (Odoo 18.0 ERP — enterprise)
v4 (Django — legacy PHP port, parallel track)
```

v1 → v2 is a direct evolution (same backend, added frontend).  
v3 is a complete rewrite on the Odoo platform.  
v4 is a parallel track — a Django port of the original PHP CodeIgniter system.

---

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        openEMIS Ecosystem                       │
│                                                                 │
│  ┌──────────────┐   ┌──────────────────────────────────────┐   │
│  │     v1       │   │                v2                    │   │
│  │  FastAPI     │   │  FastAPI Backend + Next.js Frontend  │   │
│  │  REST API    │   │                                      │   │
│  │  Port 8000   │   │  Backend: Port 8001                  │   │
│  │              │   │  Frontend: Port 3000                 │   │
│  └──────┬───────┘   └──────────────┬───────────────────────┘   │
│         │                          │                            │
│         └──────────┬───────────────┘                           │
│                    │                                            │
│              PostgreSQL DB                                      │
│                                                                 │
│  ┌──────────────────────────────┐   ┌────────────────────────┐ │
│  │            v3                │   │          v4            │ │
│  │  Odoo 18.0 ERP               │   │  Django 4.2            │ │
│  │  35+ addon modules           │   │  Traditional MVC       │ │
│  │  Port 8069                   │   │  Port 8000             │ │
│  │  OWL frontend (built-in)     │   │  Bootstrap 5 frontend  │ │
│  └──────────────────────────────┘   └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## v1 Architecture

### Pattern: Layered REST API

```
HTTP Request
    │
    ▼
FastAPI Router (app/api/v1/router.py)
    │
    ▼
Endpoint Handler (app/api/v1/endpoints/*.py)
    │
    ├── Pydantic Schema validation (app/schemas/)
    ├── JWT Auth check (app/core/security.py)
    │
    ▼
Service Layer (app/services/)
    │
    ▼
SQLAlchemy ORM (app/models/)
    │
    ▼
PostgreSQL Database
```

### Key Design Decisions
- Single-process, single-service — no microservices
- Alembic handles all schema migrations
- JWT tokens are stateless — no session store needed
- Redis used for caching hot data (analytics, dashboards)
- M-Pesa and Africa's Talking integrations are direct HTTP calls from service layer
- Static HTML dashboard served directly from FastAPI (no separate frontend process)

### Data Flow — Authentication
```
POST /api/v1/auth/login
  → validate credentials against users table
  → bcrypt password check
  → generate JWT (HS256, 30min expiry)
  → return { access_token, token_type }

Subsequent requests:
  Authorization: Bearer <token>
  → deps.py extracts and validates token
  → injects current_user into endpoint
```

---

## v2 Architecture

### Pattern: Decoupled Full-Stack

```
Browser
    │
    ▼
Next.js 14 (App Router) — Port 3000
    │
    ├── AuthGuard / RoleGuard (client-side route protection)
    ├── Zustand store (auth state)
    ├── React Query (server state, caching)
    │
    ▼
FastAPI Backend — Port 8001
    │
    ├── CORS middleware (allows localhost:3000)
    ├── JWT validation
    │
    ▼
PostgreSQL Database
```

### Key Design Decisions
- Frontend and backend are completely independent processes
- Next.js App Router with server components where possible
- React Query handles all data fetching, caching, and invalidation
- Zustand manages auth state (token, user profile) in localStorage
- shadcn/ui components built on Radix UI primitives for accessibility
- Backend models were reverse-engineered from openeducat Odoo modules — richer domain than v1

### Frontend Route Structure
```
/login                    → public
/unauthorized             → public
/(dashboard)/             → protected (AuthGuard)
  ├── /students           → role: admin, teacher
  ├── /faculty            → role: admin
  ├── /courses            → role: admin, teacher
  ├── /admissions         → role: admin
  ├── /attendance         → role: admin, teacher
  ├── /exams              → role: admin, teacher
  ├── /fees               → role: admin, accountant
  ├── /library            → role: admin, librarian
  ├── /timetable          → role: admin, teacher
  └── /reports            → role: admin
```

---

## v3 Architecture

### Pattern: Odoo ERP Modular Addon System

```
Browser
    │
    ▼
Odoo Web Client (OWL framework) — Port 8069
    │
    ├── Views: form, list, kanban, calendar, pivot, graph
    ├── Actions & Menus (defined in XML)
    │
    ▼
Odoo Server (Python)
    │
    ├── HTTP Controllers (controllers/*.py)
    ├── ORM Layer (models/*.py — inherits models.Model)
    ├── Business Logic (models methods)
    ├── Security (ir.model.access.csv + record rules)
    │
    ▼
PostgreSQL Database (Odoo manages schema via ORM)
```

### Module Dependency Graph
```
openemis_core  ◄─────────────────────────────────────────────────┐
    │                                                             │
    ├──► openemis_admission                                       │
    ├──► openemis_attendance                                      │
    ├──► openemis_exam ──► openemis_grading                       │
    ├──► openemis_fees                                            │
    ├──► openemis_timetable                                       │
    ├──► openemis_assignment                                      │
    ├──► openemis_library                                         │
    ├──► openemis_hostel                                          │
    ├──► openemis_transportation                                  │
    ├──► openemis_hr (via Odoo hr module)                         │
    ├──► openemis_lms                                             │
    ├──► openemis_lesson                                          │
    ├──► openemis_cbc ──► openemis_digiguide                      │
    ├──► openemis_mentorship                                      │
    ├──► openemis_blog                                            │
    ├──► openemis_parent                                          │
    ├──► openemis_alumni                                          │
    ├──► openemis_scholarship                                     │
    ├──► openemis_health                                          │
    ├──► openemis_discipline                                      │
    ├──► openemis_notice_board                                    │
    ├──► openemis_event                                           │
    ├──► openemis_activity                                        │
    ├──► openemis_cafeteria                                       │
    ├──► openemis_facility                                        │
    ├──► openemis_inventory                                       │
    ├──► openemis_classroom                                       │
    ├──► openemis_achievement                                     │
    └──► openemis_erp (meta-module — depends on all above)        │
                                                                  │
theme_web_openemis ───────────────────────────────────────────────┘
```

### Key Design Decisions
- Every module is independently installable — start with `openemis_core`, add others as needed
- Odoo ORM handles all migrations automatically — no Alembic
- Security is declarative: `ir.model.access.csv` defines CRUD permissions per role
- QWeb XML templates define all views — no separate frontend framework needed
- `openemis_erp` is a meta-module that simply declares dependencies on all other modules for one-click full install

---

## v4 Architecture

### Pattern: Traditional Django MVT (Model-View-Template)

```
Browser
    │
    ▼
Django URL Router (school_management/urls.py)
    │
    ├── Template Views (HTML responses via Bootstrap 5)
    └── DRF API Views (JSON responses)
         │
         ▼
    Django Views (views.py per app)
         │
         ├── Django ORM (models.py per app)
         ├── Celery Tasks (tasks.py — async email/notifications)
         │
         ▼
    SQLite (dev) / PostgreSQL (prod)
```

### App Boundaries
```
accounts/       → Custom User model, roles, JWT auth
academic/       → Classes, sections, subjects, enrollment, academic years
attendance/     → Daily attendance records, absence alerts
exams/          → Exam scheduling, marks, online exams, auto-grading
messaging/      → Private messages, group messages, file attachments
library/        → Book catalog, issue/return, overdue tracking
finance/        → Income, expenses, payments, fee management
notifications/  → In-app notifications, email dispatch via Celery
```

### Key Design Decisions
- Custom `AUTH_USER_MODEL = 'accounts.User'` — single user model with role field
- DRF provides a REST API layer alongside the traditional template views
- Celery + Redis handles all async work (email, notifications, report generation)
- SQLite for development, PostgreSQL for production (swap via `DATABASE_URL`)
- JWT via `djangorestframework-simplejwt` for API clients

---

## Cross-Version Domain Model

All four versions share the same core educational domain:

| Domain Entity | v1 | v2 | v3 | v4 |
|--------------|----|----|----|----|
| Students | ✓ | ✓ | ✓ | ✓ |
| Faculty/Teachers | ✓ | ✓ | ✓ | ✓ |
| Courses/Subjects | ✓ | ✓ | ✓ | ✓ |
| Admissions | ✓ | ✓ | ✓ | — |
| Attendance | ✓ | ✓ | ✓ | ✓ |
| Exams & Grades | ✓ | ✓ | ✓ | ✓ |
| Fees & Finance | ✓ | ✓ | ✓ | ✓ |
| Library | ✓ | ✓ | ✓ | ✓ |
| Hostel | ✓ | ✓ | ✓ | — |
| Transportation | ✓ | ✓ | ✓ | — |
| HR / Payroll | ✓ | — | ✓ | — |
| CBC Support | ✓ | ✓ | ✓ | — |
| DigiGuide | ✓ | ✓ | ✓ | — |
| Mentorship | ✓ | ✓ | ✓ | — |
| Parent Portal | ✓ | — | ✓ | ✓ |
| LMS | ✓ | ✓ | ✓ | — |
| Messaging | — | — | — | ✓ |
| Online Exams | — | — | — | ✓ |

---

## Infrastructure

### Deployment Targets

| Target | v1 | v2 | v3 | v4 |
|--------|----|----|----|----|
| Docker Compose | ✓ | — | ✓ | — |
| Kubernetes | ✓ | — | ✓ | — |
| Heroku | ✓ | — | ✓ | — |
| Native (venv) | ✓ | ✓ | ✓ | ✓ |

### Port Assignments (local development)

| Service | Port |
|---------|------|
| v1 API | 8000 |
| v2 API | 8001 |
| v2 Frontend | 3000 |
| v3 Odoo | 8069 |
| v4 Django | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |

---

## Security Architecture

See [SECURITY.md](SECURITY.md) for full details.

- v1/v2: JWT (HS256), tokens expire in 30–60 minutes, bcrypt password hashing
- v3: Odoo session-based auth + optional 2FA, record-level security rules
- v4: JWT via simplejwt + Django session auth, CSRF protection on all form views

---

## Related Documents

- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute
- [DEPLOYMENT.md](DEPLOYMENT.md) — deployment guide for all versions
- [SECURITY.md](SECURITY.md) — security practices
- [CHANGELOG.md](CHANGELOG.md) — version history
- [API_REFERENCE.md](API_REFERENCE.md) — v1 and v2 API reference
