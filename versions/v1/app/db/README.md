# app/db — Database Layer (v1)

Database engine setup and session management for the v1 FastAPI backend using SQLAlchemy + PostgreSQL.

## Files

- `base.py` — Declarative base class shared by all ORM models.
- `session.py` — SQLAlchemy engine creation and `SessionLocal` factory. Provides the `get_db()` generator used as a FastAPI dependency.
- `init_db.py` — Database initialisation script: creates all tables and seeds initial data (roles, admin user, Kenya-specific reference data).

## Usage

The database session is injected into route handlers via:

```python
from app.api.deps import get_db
db: Session = Depends(get_db)
```

Alembic is used for schema migrations — see `alembic.ini` and the `alembic/` directory at the project root.
