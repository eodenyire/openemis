# app/models — ORM Models (v2)

SQLAlchemy ORM model definitions for all EMIS entities in the v2 backend.

## Models

| File | Entities |
|---|---|
| `user.py` | User, Role — authentication and RBAC |
| `student.py` | Student, Guardian, Enrollment, ClassGroup |
| `faculty.py` | Teacher, Department, Subject, TeacherSubject |
| `admission.py` | AdmissionApplication, ApplicationDocument |
| `attendance.py` | AttendanceSession, AttendanceRecord |
| `exam.py` | ExamSession, ExamResult, GradeReport, ResultSlip |
| `fees.py` | FeeStructure, Invoice, Payment, MpesaTransaction |
| `timetable.py` | Timetable, Period, ClassSchedule |
| `library.py` | Book, BookIssue, BookReturn, BookCategory |
| `cbc.py` | CBCStrand, LearningOutcome, FormativeAssessment, Portfolio, PortfolioEntry |
| `core.py` | School, AcademicYear, Term — global reference data |

## Relationships

Models are fully relational with cascading deletes where appropriate. The `core.py` models (School, AcademicYear, Term) act as the root context for all other entities, enabling multi-school/multi-tenant support in future.
