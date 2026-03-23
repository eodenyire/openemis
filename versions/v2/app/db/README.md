# app/db — Database Layer (v2)

SQLAlchemy async database setup for the v2 backend.

## Files

- `base.py` — Declarative base class for all ORM models.
- `session.py` — Async SQLAlchemy engine and `AsyncSessionLocal` factory. Provides `get_async_db()` dependency for FastAPI.
- `init_db.py` — Schema creation and initial data seeding (roles, admin user, CBC curriculum reference data).

## v2 Upgrade

v2 uses SQLAlchemy's async engine (`asyncpg` driver) for non-blocking database I/O, improving throughput under concurrent load compared to the synchronous v1 setup.

## Migrations

Alembic handles schema migrations. Run:

```bash
alembic upgrade head
```

to apply all pending migrations against the configured PostgreSQL database.
