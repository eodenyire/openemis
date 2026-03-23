# openEMIS v4 — Django School Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

v4 is a Django-based school management system, originally converted from a PHP CodeIgniter application. It provides a traditional, monolithic web application with a multi-role system covering all aspects of school administration — from academics and attendance to library and finance.

This version was pulled from the existing [eodenyire/openemis](https://github.com/eodenyire/openemis) GitHub repository and represents the legacy web application codebase.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 4.2.7 |
| Language | Python 3.8+ |
| Database | SQLite (dev) / PostgreSQL (prod) |
| API | Django REST Framework 3.14 |
| Auth | JWT (djangorestframework-simplejwt) |
| Task Queue | Celery + Redis |
| Frontend | Bootstrap 5, jQuery |
| Email | SMTP (configurable) |

## User Roles

| Role | Capabilities |
|------|-------------|
| Admin | Complete system management |
| Teacher | Class management, attendance, exams, marks |
| Student | View results, take online exams, access materials |
| Parent | Monitor child's progress and attendance |
| Librarian | Manage books and library operations |
| Accountant | Handle payments and financial records |

## Project Structure

```
v4/
├── accounts/           # User management and authentication
├── academic/           # Classes, subjects, enrollment
├── attendance/         # Attendance tracking
├── exams/              # Examination system (traditional + online)
├── messaging/          # Communication system
├── library/            # Library management
├── finance/            # Financial management
├── notifications/      # Notification system
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── school_management/  # Django project settings & URLs
├── manage.py           # Django management entry point
├── setup.py            # Automated installation script
├── create_admin.py     # Admin user creation helper
└── requirements.txt
```

## Quick Start

### 1. Run the setup script (recommended)

```bash
python setup.py
```

This creates the virtual environment, installs dependencies, runs migrations, and sets up the project automatically.

### 2. Manual setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# or use the helper:
python create_admin.py

# Start server
python manage.py runserver
```

App: http://127.0.0.1:8000  
Admin panel: http://127.0.0.1:8000/admin

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis (for Celery task queue)
REDIS_URL=redis://localhost:6379
```

For PostgreSQL in production:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/school_db
```

## API Endpoints

| Resource | Path |
|----------|------|
| Auth | `/api/auth/` |
| Academic | `/api/academic/` |
| Attendance | `/api/attendance/` |
| Exams | `/api/exams/` |
| Messaging | `/api/messaging/` |
| Library | `/api/library/` |
| Finance | `/api/finance/` |
| Notifications | `/api/notifications/` |

## Features

- Multi-role authentication and authorization
- Academic management — classes, sections, subjects, enrollment, academic years
- Examination system — traditional exams + online exams with multiple question types, auto-grading
- Attendance tracking — daily student and teacher attendance, absence notifications
- Communication — private messaging, group messaging with file attachments, real-time notifications
- Library management — book catalog, request system, issue/return tracking, overdue notifications
- Financial management — income/expense tracking, payment records, monthly reports, fee management
- Background tasks via Celery (email notifications, report generation)

## Running Tests

```bash
python manage.py test
```

## Production Deployment

```bash
# Install production server
pip install gunicorn

# Collect static files
python manage.py collectstatic --noinput

# Start with Gunicorn
gunicorn school_management.wsgi:application --bind 0.0.0.0:8000 -w 4
```

Run behind Nginx as a reverse proxy for production use.

## Migration from PHP

This Django version is a full port of the original PHP CodeIgniter system, preserving all core functionality while providing:

- Modern Python/Django architecture
- Better security practices
- REST API layer
- Improved scalability and maintainability

## License

MIT — see [LICENSE](LICENSE).
