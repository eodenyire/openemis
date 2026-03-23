"""OpenEMIS v2 — FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v2.router import api_router
from app.db.session import engine
from app.db import registry  # noqa — registers all models with SQLAlchemy
from app.db.base import Base

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OpenEMIS v2",
    description="Education Management Information System — built from openeducat_modules",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v2")


@app.get("/")
def root():
    return {
        "app": "OpenEMIS v2",
        "version": "2.0.0",
        "docs": "/api/docs",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
