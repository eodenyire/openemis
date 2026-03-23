# app/core — Configuration & Security (v1)

Core application settings, security utilities, and shared infrastructure for the v1 FastAPI backend.

## Files

- `config.py` — Pydantic `BaseSettings` class that loads all environment variables. Covers database URL, JWT secret, M-Pesa Daraja API credentials, Africa's Talking SMS config, Redis URL, and CORS origins.
- `security.py` — Password hashing (bcrypt) and JWT token creation/verification utilities.

## Configuration Overview

| Setting | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | PostgreSQL localhost | Primary data store |
| `SECRET_KEY` | (set via env) | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | JWT lifetime |
| `MPESA_*` | (set via env) | M-Pesa payment integration |
| `AT_API_KEY` | (set via env) | Africa's Talking SMS |
| `REDIS_URL` | localhost:6379 | Caching / task queue |

All values are overridden by the `.env` file at runtime. Never commit real secrets.
