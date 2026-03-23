# openEMIS v2 — FastAPI Backend + Next.js Frontend

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](LICENSE)

## Overview

v2 is a full-stack evolution of openEMIS. It builds on the v1 FastAPI backend and adds a modern **Next.js 14** frontend with a professional component library, TypeScript, and a clean decoupled architecture. The backend was also re-engineered from the openeducat Odoo modules — reverse-engineered into a standalone FastAPI service.

## Tech Stack

### Backend
| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.115.0 |
| Language | Python 3.11 |
| Database | PostgreSQL + SQLAlchemy 2.0 |
| Auth | JWT (python-jose + passlib/bcrypt) |
| Migrations | Alembic |
| Docs | OpenAPI at `/api/docs` |

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | Next.js 14.2.5 |
| Language | TypeScript |
| Styling | Tailwind CSS + shadcn/ui |
| Components | Radix UI primitives |
| State | Zustand |
| Data Fetching | TanStack React Query + Axios |
| Forms | React Hook Form + Zod |

## Project Structure

```
v2/
├── app/                    # FastAPI backend
│   ├── api/v2/endpoints/   # Route handlers
│   ├── core/               # Config, security
│   ├── db/                 # Session, base, registry
│   ├── models/             # SQLAlchemy models
│   │   ├── core.py         # Students, faculty, courses
│   │   ├── admission.py    # Admissions
│   │   ├── attendance.py   # Attendance
│   │   ├── exam.py         # Exams
│   │   ├── fees.py         # Fees & finance
│   │   ├── lms.py          # Learning management
│   │   ├── timetable.py    # Timetable
│   │   └── ...
│   └── schemas/            # Pydantic schemas
├── web/                    # Next.js frontend
│   ├── src/
│   │   ├── app/            # Next.js app router
│   │   │   ├── (dashboard)/# Protected dashboard routes
│   │   │   ├── login/      # Auth pages
│   │   │   └── unauthorized/
│   │   ├── components/
│   │   │   ├── layout/     # AuthGuard, RoleGuard, Sidebar, Header
│   │   │   ├── shared/     # DataTable, StatCard, PageShell
│   │   │   └── ui/         # shadcn/ui components
│   │   ├── lib/            # api.ts, auth.ts, utils.ts
│   │   └── types/          # Shared TypeScript types
│   └── package.json
├── .env                    # Backend environment config
└── requirements.txt
```

## Quick Start

### Backend

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL and SECRET_KEY

# 4. Set up PostgreSQL
psql -U postgres -c "CREATE DATABASE openemis_v2;"
psql -U postgres -c "CREATE USER openemis WITH PASSWORD 'openemis';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE openemis_v2 TO openemis;"

# 5. Start the API
uvicorn app.main:app --reload --port 8001
```

API: http://localhost:8001  
Docs: http://localhost:8001/api/docs

### Frontend

```bash
cd web
npm install
npm run dev
```

Frontend: http://localhost:3000

## Environment Variables

### Backend (`.env`)
```env
DATABASE_URL=postgresql://openemis:openemis@localhost:5432/openemis_v2
SECRET_KEY=change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
APP_NAME=openEMIS v2
APP_VERSION=2.0.0
DEBUG=True
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (`web/.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## Key Differences from v1

- Decoupled frontend — Next.js replaces the static HTML served by FastAPI
- Models reverse-engineered from openeducat Odoo modules for richer domain coverage
- TypeScript frontend with full type safety
- Role-based access control via `AuthGuard` and `RoleGuard` components
- shadcn/ui component library for consistent, accessible UI

## License

LGPL-3.0 — see [LICENSE](LICENSE).
