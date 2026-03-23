# app/core — Configuration & Security (v2)

Core settings and security utilities for the v2 FastAPI backend.

## Files

- `config.py` — Pydantic `BaseSettings` loading all environment variables: database, JWT, M-Pesa, Africa's Talking SMS, Redis, and CORS.
- `security.py` — bcrypt password hashing, JWT access/refresh token creation and verification.
- `logging.py` — Structured JSON logging configuration for production observability.

## Key Settings

| Setting | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key (set via env) |
| `MPESA_*` | M-Pesa Daraja API credentials |
| `AT_API_KEY` | Africa's Talking SMS gateway |
| `REDIS_URL` | Cache and Celery broker |
| `CORS_ORIGINS` | Allowed frontend origins (Next.js dev + prod) |

## v2 Additions

- Refresh token support with rotation
- Rate limiting configuration
- Structured logging with request IDs for tracing
