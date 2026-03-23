# openEMIS v1 — Standalone FastAPI Backend

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](LICENSE)

## Overview

v1 is the first standalone Python implementation of openEMIS — a lightweight, modern REST API for educational management with **no Odoo dependency**. It was built to provide a clean, fast, and independently deployable backend that any frontend or mobile client can consume.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.115.0 |
| Language | Python 3.11 |
| Database | PostgreSQL 15 + SQLAlchemy 2.0 |
| Auth | JWT (python-jose + passlib/bcrypt) |
| Migrations | Alembic |
| Payments | M-Pesa Daraja API |
| SMS | Africa's Talking |
| Caching | Redis |
| Docs | Auto-generated OpenAPI at `/api/docs` |

## Project Structure

```
v1/
├── app/
│   ├── api/v1/endpoints/   # Route handlers
│   ├── core/               # Config, security
│   ├── db/                 # Session, base, registry
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── reports/            # PDF/Excel generation
│   └── static/             # Served HTML (login, dashboard)
├── mobile/                 # Flutter mobile companion app
├── kubernetes/             # K8s deployment manifests
├── scripts/                # Seeding, testing, deployment scripts
├── tests/                  # Pytest test suite
├── quickstart.py           # DB init + default admin creation
├── run.py                  # Dev server launcher
└── requirements.txt
```

## API Endpoints

| Resource | Base Path |
|----------|-----------|
| Auth | `/api/v1/auth/` |
| Users | `/api/v1/users/` |
| Students | `/api/v1/students/` |
| Teachers | `/api/v1/teachers/` |
| Courses | `/api/v1/courses/` |
| Subjects | `/api/v1/subjects/` |
| Admissions | `/api/v1/admissions/` |
| Attendance | `/api/v1/attendance/` |
| Exams | `/api/v1/exams/` |
| Fees | `/api/v1/fees/` |
| Library | `/api/v1/library/` |
| Hostel | `/api/v1/hostel/` |
| Transportation | `/api/v1/transportation/` |
| HR | `/api/v1/hr/` |
| Analytics | `/api/v1/analytics/` |

Full interactive docs at `http://localhost:8000/api/docs`.

## Quick Start

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
psql -U postgres -c "CREATE DATABASE openemis_db;"
psql -U postgres -c "CREATE USER openemis WITH PASSWORD 'openemis';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE openemis_db TO openemis;"

# 5. Initialize DB and create admin user
python quickstart.py

# 6. Start the server
python run.py
```

App: http://localhost:8000  
Docs: http://localhost:8000/api/docs

Default credentials after `quickstart.py`:
- Username: `admin`
- Password: `admin123`

## Docker

```bash
docker compose up -d
```

Starts PostgreSQL + the API together.

## Kubernetes

```bash
docker build -t openemis:latest .
kind load docker-image openemis:latest --name my-cluster
kubectl apply -k kubernetes/
kubectl -n openemis rollout status deployment/openemis
```

## Development

```bash
python run.py          # auto-reload dev server
pytest tests/ -v       # run tests
flake8 app/            # lint
black app/             # format
alembic upgrade head   # apply migrations
```

## Mobile App

A Flutter companion app lives in `mobile/`. It connects to this API for student-facing features (attendance, results, fees, announcements).

## License

LGPL-3.0 — see [LICENSE](LICENSE).
