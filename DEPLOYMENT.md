# Deployment Guide

This guide covers deploying all four versions of openEMIS — native, Docker, Kubernetes, and Heroku.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [v1 — FastAPI Standalone](#v1--fastapi-standalone)
3. [v2 — FastAPI + Next.js](#v2--fastapi--nextjs)
4. [v3 — Odoo 18.0](#v3--odoo-180)
5. [v4 — Django](#v4--django)
6. [Database Setup](#database-setup)
7. [Reverse Proxy (Nginx)](#reverse-proxy-nginx)
8. [Environment Variables Reference](#environment-variables-reference)

---

## Prerequisites

All versions require:
- Python 3.11 (v1, v2, v3) or Python 3.8+ (v4)
- PostgreSQL 15 (recommended for all versions)
- Git

Optional but recommended for production:
- Docker + Docker Compose
- Nginx (reverse proxy)
- Redis (v1 caching, v4 Celery)

---

## v1 — FastAPI Standalone

### Native Deployment

```bash
cd versions/v1

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL and SECRET_KEY

# Initialize database and create admin user
python quickstart.py

# Start production server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

```bash
cd versions/v1
docker compose up -d
```

This starts:
- PostgreSQL on port 5432
- FastAPI app on port 8000

### Kubernetes Deployment

```bash
cd versions/v1

# Build image
docker build -t openemis-v1:latest .

# Load into cluster (kind)
kind load docker-image openemis-v1:latest --name my-cluster

# Apply manifests
kubectl apply -k kubernetes/

# Check rollout
kubectl -n openemis rollout status deployment/openemis
```

### Heroku Deployment

```bash
cd versions/v1
heroku create openemis-v1
heroku addons:create heroku-postgresql:mini
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
```

---

## v2 — FastAPI + Next.js

### Backend (Native)

```bash
cd versions/v2

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

# Configure
cp .env.example .env   # if available, else create .env manually
# Set DATABASE_URL, SECRET_KEY, CORS_ORIGINS

# Start backend
uvicorn app.main:app --reload --port 8001
```

### Frontend (Native)

```bash
cd versions/v2/web

npm install

# Configure
cp .env.local.example .env.local   # or create manually
# Set NEXT_PUBLIC_API_URL=http://localhost:8001

# Development
npm run dev

# Production build
npm run build
npm start
```

### Production Frontend with PM2

```bash
npm install -g pm2
npm run build
pm2 start npm --name "openemis-v2-web" -- start
pm2 save
pm2 startup
```

### Environment Variables

Backend `.env`:
```env
DATABASE_URL=postgresql://openemis:password@localhost:5432/openemis_v2
SECRET_KEY=your-long-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=["https://yourdomain.com"]
DEBUG=False
```

Frontend `web/.env.local`:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## v3 — Odoo 18.0

### Prerequisites

```bash
# Install Odoo 18.0 source
git clone --depth 1 --branch 18.0 https://github.com/odoo/odoo.git /opt/odoo18

# Create virtual environment
python3.11 -m venv /opt/odoo18/venv
source /opt/odoo18/venv/bin/activate

# Install Odoo dependencies
pip install setuptools wheel
pip install -r /opt/odoo18/requirements.txt
```

### Native Deployment

1. Set up PostgreSQL (see [Database Setup](#database-setup))

2. Create Odoo config at `/etc/odoo/odoo.conf`:
   ```ini
   [options]
   addons_path = /opt/odoo18/addons,/path/to/versions/v3
   db_host = localhost
   db_port = 5432
   db_user = odoo
   db_password = your-db-password
   db_name = openemis_odoo
   http_port = 8069
   log_level = warn
   log_file = /var/log/odoo/odoo.log
   list_db = False
   admin_passwd = your-master-password-hash
   workers = 4
   max_cron_threads = 2
   ```

3. Initialize and install modules:
   ```bash
   /opt/odoo18/venv/bin/python /opt/odoo18/odoo-bin \
     -c /etc/odoo/odoo.conf \
     -i openemis_erp \
     --stop-after-init
   ```

4. Start Odoo:
   ```bash
   /opt/odoo18/venv/bin/python /opt/odoo18/odoo-bin -c /etc/odoo/odoo.conf
   ```

### Systemd Service (Linux)

Create `/etc/systemd/system/odoo.service`:
```ini
[Unit]
Description=Odoo 18.0 — openEMIS
After=network.target postgresql.service

[Service]
Type=simple
User=odoo
Group=odoo
ExecStart=/opt/odoo18/venv/bin/python /opt/odoo18/odoo-bin -c /etc/odoo/odoo.conf
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable odoo
systemctl start odoo
```

### Docker Deployment

```bash
cd versions/v3
docker compose up -d
```

### Kubernetes Deployment

```bash
cd versions/v3
docker build -t openemis-v3:latest .
kind load docker-image openemis-v3:latest --name openemis-local
kubectl apply -k kubernetes/
kubectl -n openemis rollout status deployment/openemis --timeout=300s
```

### Heroku Deployment

```bash
cd versions/v3
heroku create openemis-v3
heroku addons:create heroku-postgresql:standard-0
git push heroku main
```

---

## v4 — Django

### Native Deployment

```bash
cd versions/v4

# Automated setup (recommended)
python setup.py

# Or manual:
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env — set SECRET_KEY, DATABASE_URL, email settings

python manage.py migrate
python create_admin.py   # or: python manage.py createsuperuser

# Development
python manage.py runserver

# Production
pip install gunicorn
python manage.py collectstatic --noinput
gunicorn school_management.wsgi:application --bind 0.0.0.0:8000 -w 4
```

### Celery Worker (for background tasks)

```bash
# In a separate terminal/process
celery -A school_management worker --loglevel=info

# Celery Beat (scheduled tasks)
celery -A school_management beat --loglevel=info
```

### Systemd Service for Celery

```ini
[Unit]
Description=openEMIS v4 Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/versions/v4
ExecStart=/path/to/venv/bin/celery -A school_management worker --loglevel=info
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## Database Setup

### PostgreSQL — All Versions

```sql
-- v1
CREATE USER openemis WITH PASSWORD 'strong-password';
CREATE DATABASE openemis_db OWNER openemis;
GRANT ALL PRIVILEGES ON DATABASE openemis_db TO openemis;

-- v2
CREATE DATABASE openemis_v2 OWNER openemis;
GRANT ALL PRIVILEGES ON DATABASE openemis_v2 TO openemis;

-- v3 (Odoo)
CREATE USER odoo WITH SUPERUSER PASSWORD 'strong-password';
CREATE DATABASE openemis_odoo OWNER odoo;

-- v4
CREATE USER school WITH PASSWORD 'strong-password';
CREATE DATABASE school_db OWNER school;
GRANT ALL PRIVILEGES ON DATABASE school_db TO school;
```

### Backups

```bash
# Backup
pg_dump -U openemis openemis_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U openemis openemis_db < backup_20240101.sql

# Odoo backup (includes filestore)
python /opt/odoo18/odoo-bin -c odoo.conf --stop-after-init \
  --database openemis_odoo --backup-format zip \
  --backup-dir /backups/
```

---

## Reverse Proxy (Nginx)

### v1 — FastAPI on port 8000

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### v3 — Odoo on port 8069

```nginx
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoochat {
    server 127.0.0.1:8072;
}

server {
    listen 443 ssl;
    server_name erp.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/erp.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.yourdomain.com/privkey.pem;

    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    location /longpolling {
        proxy_pass http://odoochat;
    }

    location / {
        proxy_pass http://odoo;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }

    gzip on;
    gzip_types text/css text/less text/plain text/xml application/xml application/json application/javascript;
}
```

---

## Environment Variables Reference

### v1 / v2 Backend

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `SECRET_KEY` | Yes | JWT signing key — use a long random string |
| `ALGORITHM` | No | JWT algorithm (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token lifetime (default: 30 for v1, 60 for v2) |
| `CORS_ORIGINS` | No | JSON array of allowed origins |
| `DEBUG` | No | `True` for dev, `False` for prod |
| `REDIS_URL` | No | Redis connection (v1 only, for caching) |
| `MPESA_CONSUMER_KEY` | No | M-Pesa Daraja API key (v1 only) |
| `MPESA_CONSUMER_SECRET` | No | M-Pesa Daraja API secret (v1 only) |
| `AT_API_KEY` | No | Africa's Talking API key (v1 only) |

### v2 Frontend

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API base URL |

### v4 Django

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | No | `True` for dev, `False` for prod |
| `DATABASE_URL` | No | Database connection (default: SQLite) |
| `EMAIL_HOST` | No | SMTP server |
| `EMAIL_HOST_USER` | No | SMTP username |
| `EMAIL_HOST_PASSWORD` | No | SMTP password |
| `REDIS_URL` | No | Redis URL for Celery |
