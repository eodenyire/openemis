from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings

# Register all models BEFORE creating tables
import app.db.registry  # noqa: F401

from app.db.base import Base
from app.db.session import engine
from app.api.v1.router import api_router

# Create all tables on startup
Base.metadata.create_all(bind=engine)

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Open Source Educational Management Information System – Standalone Python Edition",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router, prefix="/api/v1")

# Serve the login page at /
@app.get("/", include_in_schema=False)
async def login_page():
    return FileResponse(STATIC_DIR / "index.html")

# Serve the dashboard at /dashboard
@app.get("/dashboard", include_in_schema=False)
async def dashboard_page():
    return FileResponse(STATIC_DIR / "dashboard.html")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Mount static files last (catches everything else in /static/)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
