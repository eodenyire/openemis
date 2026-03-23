# v4 Architecture — Django School Management System

## Overview

v4 is a traditional Django MVT (Model-View-Template) application. It provides both a server-rendered HTML web interface (Bootstrap 5) and a REST API layer (Django REST Framework). It was ported from a PHP CodeIgniter application and preserves the original multi-role school management structure.

---

## System Diagram

```
Browser
    │
    ├── HTML requests → Django Views → Templates (Bootstrap 5)
    └── API requests  → DRF ViewSets → JSON responses
         │
         ▼
Django URL Router (school_management/urls.py)
    │
    ├── accounts/urls.py      → auth, user management
    ├── academic/urls.py      → classes, subjects, enrollment
    ├── attendance/urls.py    → attendance records
    ├── exams/urls.py         → exams, marks, online exams
    ├── messaging/urls.py     → messages, group chats
    ├── library/urls.py       → books, issue/return
    ├── finance/urls.py       → payments, fees
    └── notifications/urls.py → in-app notifications
         │
         ▼
Django ORM (models.py per app)
    │
    ├── Celery Tasks (async: email, notifications, reports)
    │
    ▼
SQLite (dev) / PostgreSQL (prod)
```

---

## App Structure

Each Django app follows the standard layout:

```
<app>/
├── models.py        # Database models
├── views.py         # View functions / class-based views
├── serializers.py   # DRF serializers (API layer)
├── urls.py          # URL routing
├── forms.py         # Django forms (HTML interface)
├── tasks.py         # Celery async tasks
├── admin.py         # Django admin registration
├── tests.py         # Unit tests
└── migrations/      # Database migrations
```

---

## App Responsibilities

### `accounts` — Authentication & Users

```
User (custom AUTH_USER_MODEL)
    ├── role: admin | teacher | student | parent | librarian | accountant
    ├── profile fields: name, phone, address, photo
    └── relationships to other models

UserProfile (extended profile data)
```

- Custom `AbstractUser` with `role` field
- JWT authentication via `djangorestframework-simplejwt`
- Django session auth for web views
- Role-based permission mixins for views

### `academic` — Academic Structure

```
AcademicYear
    └── AcademicTerm
         └── Class (grade/stream)
              ├── Subject
              ├── Enrollment (Student ↔ Class)
              └── TeacherAssignment (Teacher ↔ Subject ↔ Class)
```

### `attendance` — Attendance Tracking

```
AttendanceRecord
    ├── student (FK → accounts.User)
    ├── class (FK → academic.Class)
    ├── date
    ├── status: present | absent | late | excused
    └── remarks
```

Celery task: sends absence notification email to parent when student is marked absent.

### `exams` — Examination System

```
Exam
    ├── ExamSchedule (Exam ↔ Subject ↔ Class ↔ date/time)
    ├── ExamResult (Student ↔ Exam ↔ Subject ↔ marks)
    └── OnlineExam
         ├── Question (multiple choice, true/false, short answer)
         ├── StudentAttempt
         └── Answer (auto-graded for MCQ/T-F)
```

### `messaging` — Communication

```
Message
    ├── sender (FK → User)
    ├── recipient (FK → User)  ← private message
    ├── group (FK → MessageGroup)  ← group message
    ├── content
    └── attachments (FileField)

MessageGroup
    └── members (M2M → User)
```

### `library` — Library Management

```
Book
    ├── BookCopy (physical copies)
    ├── BookIssue (Student ↔ BookCopy ↔ issue_date ↔ due_date)
    └── BookReturn

Celery task: daily check for overdue books, sends reminder emails.
```

### `finance` — Financial Management

```
FeeStructure
    └── FeeRecord (Student ↔ FeeStructure ↔ amount ↔ due_date)

Payment
    ├── student (FK → User)
    ├── amount
    ├── payment_date
    └── receipt_number

Expense
    ├── category
    ├── amount
    └── date
```

### `notifications` — Notification System

```
Notification
    ├── recipient (FK → User)
    ├── type: info | warning | success | error
    ├── message
    ├── is_read
    └── created_at
```

Celery tasks dispatch email notifications for:
- Absence alerts (to parents)
- Exam result publication
- Fee payment reminders
- Library overdue notices
- New messages

---

## Authentication Flow

### Web (Session-based)

```
POST /accounts/login/
  → Django authenticate(username, password)
  → login(request, user)  ← creates session cookie
  → redirect to dashboard

Protected views:
  → @login_required decorator
  → LoginRequiredMixin for class-based views
  → Role check via custom mixin
```

### API (JWT)

```
POST /api/auth/token/
  → simplejwt validates credentials
  → returns { access, refresh }

POST /api/auth/token/refresh/
  → returns new access token

Protected API endpoints:
  → IsAuthenticated permission class
  → JWT token in Authorization: Bearer header
```

---

## REST API Layer

DRF ViewSets provide the API:

```python
class StudentViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role='student')
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        # Teachers see only their class students
        if self.request.user.role == 'teacher':
            return self.queryset.filter(class__teacher=self.request.user)
        return self.queryset
```

---

## Celery Architecture

```
Django App
    │
    └── task.delay() / task.apply_async()
         │
         ▼
Redis (message broker)
         │
         ▼
Celery Worker (separate process)
    ├── send_absence_notification()
    ├── send_overdue_reminder()
    ├── generate_report()
    └── send_bulk_email()
```

Start workers:
```bash
celery -A school_management worker --loglevel=info
celery -A school_management beat --loglevel=info   # scheduled tasks
```

---

## Database Configuration

Development (default):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Production (PostgreSQL via `DATABASE_URL`):
```python
import dj_database_url
DATABASES = {'default': dj_database_url.parse(os.environ['DATABASE_URL'])}
```

---

## Static Files

- Development: served by Django's `runserver`
- Production: `python manage.py collectstatic` → serve via Nginx

```
static/          → source static files (CSS, JS, images)
staticfiles/     → collected output (production)
media/           → user-uploaded files (profile photos, attachments)
```

---

## Security Configuration

Key Django security settings for production:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```
