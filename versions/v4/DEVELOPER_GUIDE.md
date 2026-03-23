# v4 Developer Guide — Django

## Setup

```bash
cd versions/v4

# Automated setup (recommended)
python setup.py

# Or manual:
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/macOS

pip install -r requirements.txt

cp .env.example .env
# Edit .env — set SECRET_KEY at minimum

python manage.py migrate
python create_admin.py   # creates admin user

python manage.py runserver
```

App: http://127.0.0.1:8000  
Admin: http://127.0.0.1:8000/admin

Default admin credentials (after `create_admin.py`): check the script output.

---

## Project Layout

```
versions/v4/
├── school_management/   # Django project (settings, urls, wsgi)
├── accounts/            # Users, auth, roles
├── academic/            # Classes, subjects, enrollment
├── attendance/          # Attendance records
├── exams/               # Exams, marks, online exams
├── messaging/           # Messages, group chats
├── library/             # Books, issue/return
├── finance/             # Payments, fees
├── notifications/       # In-app notifications
├── templates/           # HTML templates (shared)
├── static/              # CSS, JS, images
├── manage.py
└── requirements.txt
```

---

## Adding a New Django App

### 1. Create the app

```bash
python manage.py startapp myapp
```

### 2. Register in settings

`school_management/settings.py`:
```python
LOCAL_APPS = [
    ...
    'myapp',
]
```

### 3. Create the model

`myapp/models.py`:
```python
from django.db import models
from accounts.models import User

class MyModel(models.Model):
    name = models.CharField(max_length=255)
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='my_models'
    )
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'My Model'
        verbose_name_plural = 'My Models'

    def __str__(self):
        return f"{self.name} — {self.student}"
```

### 4. Create and apply migration

```bash
python manage.py makemigrations myapp
python manage.py migrate
```

### 5. Create the DRF serializer

`myapp/serializers.py`:
```python
from rest_framework import serializers
from .models import MyModel

class MyModelSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = MyModel
        fields = ['id', 'name', 'student', 'student_name', 'date', 'notes']
```

### 6. Create views

`myapp/views.py`:
```python
from rest_framework import viewsets, permissions
from .models import MyModel
from .serializers import MyModelSerializer

class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return self.queryset.filter(student=user)
        return self.queryset
```

### 7. Create URLs

`myapp/urls.py`:
```python
from rest_framework.routers import DefaultRouter
from .views import MyModelViewSet

router = DefaultRouter()
router.register(r'my-models', MyModelViewSet)

urlpatterns = router.urls
```

### 8. Register in main URLs

`school_management/urls.py`:
```python
path('api/myapp/', include('myapp.urls')),
```

### 9. Register in admin

`myapp/admin.py`:
```python
from django.contrib import admin
from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'student', 'date']
    list_filter = ['date']
    search_fields = ['name', 'student__username']
```

---

## Adding a Celery Task

`myapp/tasks.py`:
```python
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def notify_student(student_id: int, message: str):
    """Send email notification to a student."""
    from accounts.models import User
    student = User.objects.get(id=student_id)
    send_mail(
        subject='openEMIS Notification',
        message=message,
        from_email='noreply@openemis.org',
        recipient_list=[student.email],
        fail_silently=False,
    )
```

Call it from a view:
```python
from myapp.tasks import notify_student

# Async (background)
notify_student.delay(student_id=student.id, message="Your result is ready.")

# Scheduled (in celery beat config)
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'daily-overdue-check': {
        'task': 'library.tasks.check_overdue_books',
        'schedule': crontab(hour=8, minute=0),
    },
}
```

---

## Role-Based Access Control

### In views

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class AdminOnlyView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
```

### In DRF

```python
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'

class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ('teacher', 'admin')
```

---

## Running Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test accounts

# Specific test class
python manage.py test accounts.tests.UserModelTest

# With verbosity
python manage.py test -v 2
```

Write tests in `myapp/tests.py`:
```python
from django.test import TestCase
from accounts.models import User

class MyModelTest(TestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            username='student1',
            password='testpass',
            role='student'
        )

    def test_create_my_model(self):
        from myapp.models import MyModel
        obj = MyModel.objects.create(name='Test', student=self.student)
        self.assertEqual(str(obj), f"Test — {self.student}")
```

---

## Database Migrations

```bash
# Create migrations for all apps
python manage.py makemigrations

# Create for specific app
python manage.py makemigrations myapp

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Roll back
python manage.py migrate myapp 0001  # roll back to migration 0001
```

---

## Django Shell

```bash
python manage.py shell

# In the shell:
from accounts.models import User
User.objects.filter(role='student').count()

from academic.models import Class
Class.objects.all()
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | No | `True` for dev (default), `False` for prod |
| `DATABASE_URL` | No | DB connection (default: SQLite) |
| `EMAIL_HOST` | No | SMTP server |
| `EMAIL_HOST_USER` | No | SMTP username |
| `EMAIL_HOST_PASSWORD` | No | SMTP password |
| `REDIS_URL` | No | Redis for Celery (default: `redis://localhost:6379`) |

---

## Production Checklist

```bash
# Collect static files
python manage.py collectstatic --noinput

# Check for deployment issues
python manage.py check --deploy

# Start Gunicorn
gunicorn school_management.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120

# Start Celery worker
celery -A school_management worker --loglevel=warn --concurrency=4

# Start Celery beat (scheduled tasks)
celery -A school_management beat --loglevel=warn
```
