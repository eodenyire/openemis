# app/api — REST API Layer (v1)

This folder contains the FastAPI route definitions and dependency injection for the v1 CBC EMIS Kenya backend.

## Structure

- `deps.py` — Shared FastAPI dependencies: database session injection, current user extraction from JWT token, role-based access guards.
- `crud.py` — Generic CRUD helper functions used across multiple route modules.
- `v1/` — Versioned API routes grouped by domain (students, faculty, admissions, attendance, exams, fees, timetable, library, etc.).

## How It Works

Routes are registered in `app/main.py` under the `/api/v1` prefix. Each sub-module in `v1/` maps to a specific EMIS domain and exposes standard REST endpoints (GET, POST, PUT, DELETE). Authentication is enforced via JWT bearer tokens validated in `deps.py`.

## Key Patterns

- Dependency injection via `Depends()` for DB sessions and auth
- Role guards: `admin`, `teacher`, `student`, `parent` roles enforced per endpoint
- Pydantic schemas from `app/schemas/` used for request/response validation
