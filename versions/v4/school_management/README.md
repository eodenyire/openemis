# school_management — Django Project Root (v4)

The Django project configuration package — the entry point that wires together all apps, middleware, and settings.

## Files

| File | Purpose |
|---|---|
| `settings.py` | All Django settings: installed apps, database, REST framework, JWT, CORS, email, Celery |
| `urls.py` | Root URL configuration — includes URL patterns from all installed apps |
| `wsgi.py` | WSGI entry point for production deployment (Gunicorn, uWSGI) |
| `__init__.py` | Package marker |

## Installed Apps

The project registers 8 local apps:
`accounts`, `academic`, `attendance`, `exams`, `messaging`, `library`, `finance`, `notifications`

Plus third-party: `rest_framework`, `corsheaders`, `rest_framework_simplejwt`

## Key Configuration

| Setting | Value |
|---|---|
| Database | SQLite (dev) — swap to PostgreSQL for production |
| Auth model | Custom `accounts.User` |
| API auth | JWT via `djangorestframework-simplejwt` (60 min access, 7 day refresh) |
| CORS | Allows `localhost:3000` for Next.js frontend dev |
| Pagination | 20 items per page |

## Running

```bash
python manage.py migrate
python manage.py runserver
```
