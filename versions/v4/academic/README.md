# academic — Academic Management (v4)

Django app managing the core academic structure — classes, sections, subjects, enrollment, and academic years.

## Files
- `models.py` — `Class`, `Section`, `Subject`, `AcademicYear`, `StudentEnrollment`, `SubjectAssignment`
- `views.py` — CRUD views for all academic resources
- `urls.py` — Academic URL patterns
- `admin.py` — Admin registration

## Models
- `Class` — Class definitions (Grade 1, Grade 2, etc.)
- `Section` — Sections within a class (A, B, C)
- `Subject` — Subject definitions with class assignment
- `AcademicYear` — Academic year management
- `StudentEnrollment` — Student-class-year enrollment records
- `SubjectAssignment` — Teacher-subject-class assignments

## API
Exposes REST endpoints at `/api/academic/` for all resources.
