# attendance — Attendance Tracking (v4)

Django app for daily student and teacher attendance management.

## Files
- `models.py` — `StudentAttendance`, `TeacherAttendance`
- `views.py` — Attendance entry, reports, and summary views
- `urls.py` — Attendance URL patterns
- `admin.py` — Admin registration

## Models
- `StudentAttendance` — Daily attendance per student (present/absent/late), linked to class and date
- `TeacherAttendance` — Teacher daily attendance records

## Key Features
- Bulk attendance entry per class and date
- Attendance percentage calculation per student
- Absence notification triggers (via Celery)
- Attendance reports by student, class, and date range

## API
REST endpoints at `/api/attendance/`.
