"""Startup diagnostics — run with: .venv/Scripts/python.exe scripts/diagnose.py"""
import sys
print(f"Python: {sys.version}")

# 1. Config
try:
    from app.core.config import settings
    print(f"[OK] Config loaded. DB: {settings.DATABASE_URL[:50]}")
except Exception as e:
    print(f"[FAIL] Config: {e}")
    sys.exit(1)

# 2. DB connection
try:
    from app.db.session import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("[OK] Database connection")
except Exception as e:
    print(f"[FAIL] Database: {e}")
    sys.exit(1)

# 3. Model imports
try:
    import app.db.registry  # noqa
    print("[OK] Models imported")
except Exception as e:
    print(f"[FAIL] Models: {e}")
    sys.exit(1)

# 4. Table creation
try:
    from app.db.base import Base
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables OK")
except Exception as e:
    print(f"[FAIL] Tables: {e}")
    sys.exit(1)

# 5. Router imports
try:
    from app.api.v1.router import api_router
    routes = [r.path for r in api_router.routes]
    print(f"[OK] Router loaded — {len(routes)} routes")
except Exception as e:
    print(f"[FAIL] Router: {e}")
    sys.exit(1)

# 6. Full app import
try:
    from app.main import app
    print("[OK] FastAPI app created")
except Exception as e:
    print(f"[FAIL] App: {e}")
    sys.exit(1)

print("\nAll checks passed. Safe to start uvicorn.")
