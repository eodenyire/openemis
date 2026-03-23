# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in openEMIS, please do **not** open a public GitHub issue.

Instead, email: **support@openemis.org**

Include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Which version(s) are affected

We will acknowledge your report within 48 hours and aim to release a fix within 14 days for critical issues.

---

## Security Architecture by Version

### v1 — FastAPI

**Authentication**
- JWT tokens using HS256 algorithm
- Tokens expire after 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Passwords hashed with bcrypt (passlib)
- No refresh tokens — users re-authenticate after expiry

**Authorization**
- Role-based: `admin`, `teacher`, `student`, `parent`, `staff`
- Role checked in dependency injection (`app/api/deps.py`)
- Endpoint-level guards using FastAPI `Depends()`

**Transport**
- CORS configured via `CORS_ORIGINS` — restrict to known frontend origins in production
- Run behind HTTPS reverse proxy (Nginx/Caddy) in production

**Secrets Management**
- All secrets via environment variables (`.env` file, never committed)
- `SECRET_KEY` must be a long random string in production
- M-Pesa and Africa's Talking credentials via env vars

### v2 — FastAPI + Next.js

**Authentication**
- Same JWT approach as v1 (HS256, 60-minute expiry)
- Frontend stores token in `localStorage` via Zustand
- Token sent as `Authorization: Bearer <token>` header on every API request

**Authorization**
- Backend: same role-based dependency injection as v1
- Frontend: `AuthGuard` redirects unauthenticated users to `/login`
- `RoleGuard` restricts pages by role — unauthorized users see `/unauthorized`

**Frontend Security**
- No secrets in frontend code — only `NEXT_PUBLIC_API_URL` is exposed
- All sensitive operations go through the backend API
- Zod validation on all form inputs before submission

**CORS**
- Backend allows `localhost:3000` in development
- In production, set `CORS_ORIGINS` to your actual frontend domain only

### v3 — Odoo 18.0

**Authentication**
- Odoo session-based authentication (cookie)
- Optional two-factor authentication (TOTP) via Odoo's built-in 2FA
- Passwords hashed with PBKDF2

**Authorization**
- Declarative security via `ir.model.access.csv` — defines Create/Read/Write/Delete per model per group
- Record rules (`ir.rule`) for row-level security (e.g., students can only see their own records)
- Odoo groups map to openEMIS roles: `openemis_core.group_student`, `openemis_core.group_teacher`, `openemis_core.group_admin`

**Odoo-Specific**
- Never expose the Odoo master password — used for database management
- Disable the database manager in production: set `list_db = False` in `odoo.conf`
- Use `dbfilter` to restrict which databases are accessible

**Secrets Management**
- Database credentials in `odoo.conf` — restrict file permissions (`chmod 640`)
- Never run Odoo as root

### v4 — Django

**Authentication**
- Django session authentication for web views
- JWT via `djangorestframework-simplejwt` for API clients
- Access tokens expire in 60 minutes, refresh tokens in 7 days
- Rotate refresh tokens enabled

**Authorization**
- Custom `AUTH_USER_MODEL` with `role` field
- Django's built-in permission system + custom role checks in views
- DRF `IsAuthenticated` as default permission class

**Django Security Middleware**
- `SecurityMiddleware` — HTTPS redirect, HSTS headers
- `CsrfViewMiddleware` — CSRF protection on all form submissions
- `XFrameOptionsMiddleware` — clickjacking protection

**Secrets Management**
- `SECRET_KEY` via `python-decouple` from `.env`
- Never commit `.env` — use `.env.example` as template
- Email credentials via env vars

---

## General Security Practices

### Never Commit Secrets
All versions use `.env` files for secrets. These are in `.gitignore`. Never commit:
- `SECRET_KEY` values
- Database passwords
- API keys (M-Pesa, Africa's Talking, SMTP)
- Odoo master password

### Production Checklist

**All versions:**
- [ ] `DEBUG = False`
- [ ] Strong, unique `SECRET_KEY` (50+ random characters)
- [ ] Database password is not the default (`openemis`/`odoo`)
- [ ] HTTPS enabled (TLS certificate)
- [ ] CORS restricted to actual frontend domain
- [ ] Firewall: only expose necessary ports (80, 443)
- [ ] Database not exposed to public internet

**v1/v2 specific:**
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` set appropriately (30–60 minutes)
- [ ] Redis password set if Redis is network-accessible

**v3 (Odoo) specific:**
- [ ] `list_db = False` in `odoo.conf`
- [ ] Odoo master password changed from default
- [ ] `admin_passwd` in `odoo.conf` is a strong hash
- [ ] PostgreSQL `odoo` user has minimal required privileges

**v4 (Django) specific:**
- [ ] `ALLOWED_HOSTS` set to actual domain (not `*`)
- [ ] `SECURE_SSL_REDIRECT = True` in production
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] Static files served by Nginx, not Django

### Dependency Updates
- Regularly update dependencies to patch known CVEs
- Use `pip audit` (v1/v2/v4) or `safety check` to scan for vulnerable packages
- Odoo v3: keep Odoo version updated for security patches

---

## Supported Versions

| Version | Security Support |
|---------|-----------------|
| v4 (Django) | Active |
| v3 (Odoo 18.0) | Active |
| v2 (FastAPI + Next.js) | Active |
| v1 (FastAPI standalone) | Maintenance only |
