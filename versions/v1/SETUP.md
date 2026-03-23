# openEMIS Setup Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 15+

## Installation

### 1. Clone and set up environment

```bash
git clone https://github.com/eodenyire/openEMIS.git
cd openEMIS
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:
- `DATABASE_URL` – your PostgreSQL connection string
- `SECRET_KEY` – a strong random string for JWT signing

### 3. Set up PostgreSQL

```sql
CREATE DATABASE openemis_db;
CREATE USER openemis WITH PASSWORD 'openemis';
GRANT ALL PRIVILEGES ON DATABASE openemis_db TO openemis;
```

### 4. Initialise and start

```bash
python quickstart.py   # creates tables + default admin user
python run.py          # starts the dev server on port 8000
```

Open http://localhost:8000 — login page is served there.
API docs at http://localhost:8000/api/docs.

---

## Docker

```bash
docker compose up -d
```

Everything (Postgres + API) starts together. App at http://localhost:8000.

---

## Production

For production deployments:

1. Set `DEBUG=False` in your environment
2. Use a strong `SECRET_KEY`
3. Run behind a reverse proxy (nginx, Caddy)
4. Use `gunicorn` with uvicorn workers:

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Database Migrations

```bash
# Generate a migration after model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

---

## Default Credentials

After running `quickstart.py`:
- Username: `admin`
- Password: `admin123`

Change the password immediately after first login.
