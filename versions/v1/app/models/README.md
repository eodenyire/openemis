# app/models — ORM Models (v1)

SQLAlchemy ORM model definitions for all EMIS entities in the v1 backend.

## Domain Models

| File | Entities |
|---|---|
| `user.py` | User, Role, UserRole — authentication and RBAC |
| `student.py` | Student, Guardian, Enrollment |
| `faculty.py` | Teacher, Department, Subject |
| `admission.py` | AdmissionApplication, ApplicationStatus |
| `attendance.py` | AttendanceRecord, AttendanceSession |
| `exam.py` | ExamSession, ExamResult, GradeReport |
| `fees.py` | FeeStructure, Invoice, Payment, MpesaTransaction |
| `timetable.py` | Timetable, Period, ClassSchedule |
| `library.py` | Book, BookIssue, BookReturn |
| `cbc.py` | CBCStrand, LearningOutcome, FormativeAssessment, Portfolio |

## Relationships

All models inherit from `Base` in `app/db/base.py`. Foreign keys link students to enrollments, enrollments to classes, classes to timetables, and so on — forming a complete school data graph.

These models are the source of truth for the PostgreSQL schema. Alembic migrations are generated from changes here.
