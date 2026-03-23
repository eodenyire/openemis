# Changelog

All notable changes to openEMIS are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### In Progress
- Comprehensive documentation across all versions
- GitHub Actions CI/CD pipeline for v1 and v2
- v2 frontend — remaining dashboard pages (HR, payroll, reports)

---

## [v4.0.0] — Django School Management System

### Added
- Full Django 4.2 port of the original PHP CodeIgniter school management system
- Multi-role authentication: Admin, Teacher, Student, Parent, Librarian, Accountant
- Custom `AUTH_USER_MODEL` with role-based permissions
- Academic management: classes, sections, subjects, enrollment, academic years
- Examination system: traditional exams + online exams with multiple question types and auto-grading
- Attendance tracking with absence notifications
- Private and group messaging with file attachments
- Library management: book catalog, issue/return, overdue notifications
- Financial management: income/expense tracking, payment records, monthly reports
- Background task processing via Celery + Redis
- Django REST Framework API layer with JWT authentication
- Bootstrap 5 frontend with responsive design
- Automated setup script (`setup.py`)
- Admin user creation helper (`create_admin.py`)

### Tech Stack
- Django 4.2.7, Python 3.8+
- SQLite (dev) / PostgreSQL (prod)
- DRF 3.14, djangorestframework-simplejwt
- Celery + Redis
- Bootstrap 5, jQuery

---

## [v3.0.0] — Odoo 18.0 Modular ERP

### Added
- Full suite of 35+ Odoo 18.0 addon modules
- `openemis_core` — foundation module: students, courses, subjects, faculties, academic years and terms
- `openemis_admission` — admissions and enrolment workflow
- `openemis_attendance` — student and faculty attendance tracking
- `openemis_exam` — examination scheduling, mark sheets, grade configuration
- `openemis_fees` — fee structure, invoicing, payment tracking
- `openemis_timetable` — class timetable generation and management
- `openemis_assignment` — assignment creation, submission, grading
- `openemis_library` — library management with CBC grade-level categorisation
- `openemis_lms` — Learning Management System
- `openemis_cbc` — Competency-Based Curriculum (CBC) support
- `openemis_digiguide` — Digital Career Guidance with KUCCPS integration and national exam prediction
- `openemis_mentorship` — mentorship platform with DMs and group forums
- `openemis_blog` — educational blog for mentors, teachers, and professionals
- `openemis_parent` — parent portal and parent–student linking
- `openemis_hostel` — hostel accommodation management
- `openemis_transportation` — transport logistics management
- `openemis_health` — student health records
- `openemis_discipline` — student discipline management
- `openemis_scholarship` — scholarship management
- `openemis_alumni` — alumni management
- `openemis_notice_board` — notice board and announcements
- `openemis_event` — events management
- `openemis_activity` — extra-curricular activities
- `openemis_cafeteria` — cafeteria management
- `openemis_facility` — school facilities management
- `openemis_inventory` — inventory management
- `openemis_classroom` — classroom management
- `openemis_achievement` — student achievements
- `openemis_grading` — grading system configuration
- `openemis_erp` — meta-module bundling all modules for one-click install
- `theme_web_openemis` — custom UI theme
- Docker Compose deployment
- Kubernetes manifests
- Heroku deployment config
- GitHub Actions CI/CD workflows
- Demo data generation script (100 classrooms, 100 staff, 100 students per class)
- Comprehensive test suite (unit, integration, API, snapshot)

### Tech Stack
- Odoo 18.0, Python 3.11
- PostgreSQL 15
- QWeb XML templates
- Odoo OWL frontend framework

---

## [v2.0.0] — FastAPI + Next.js Full-Stack

### Added
- Next.js 14 frontend with App Router
- TypeScript throughout the frontend
- Tailwind CSS + shadcn/ui component library
- Radix UI primitives for accessible components
- Zustand for auth state management
- TanStack React Query for server state and caching
- React Hook Form + Zod for form validation
- AuthGuard and RoleGuard components for route protection
- Role-based access control on frontend routes
- Backend models reverse-engineered from openeducat Odoo modules
- New API endpoints: activities, alumni, digiguide, events, facilities, health, hostel, lms, mentorship, noticeboard, scholarships, timetable, transport
- Decoupled architecture — frontend and backend are independent processes
- v2 API at `/api/v2/` (separate from v1's `/api/v1/`)

### Changed
- Backend port moved to 8001 (v1 stays on 8000)
- JWT token expiry extended to 60 minutes (was 30 in v1)
- Static HTML dashboard replaced by Next.js frontend

### Tech Stack
- FastAPI 0.115.0, Python 3.11
- Next.js 14.2.5, TypeScript
- PostgreSQL + SQLAlchemy 2.0
- Tailwind CSS, shadcn/ui, Radix UI
- Zustand, React Query, Axios

---

## [v1.0.0] — Standalone FastAPI Backend

### Added
- FastAPI REST API with 50+ endpoints
- JWT authentication (HS256, 30-minute tokens)
- bcrypt password hashing
- PostgreSQL database with SQLAlchemy 2.0 ORM
- Alembic database migrations
- Core modules: students, teachers, courses, subjects, admissions, attendance, exams, fees
- Extended modules: library, hostel, transportation, HR, analytics
- Kenya-specific integrations: M-Pesa Daraja API, Africa's Talking SMS, NEMIS, KNEC, TPAD
- CBC (Competency-Based Curriculum) support
- DigiGuide career guidance module
- Mentorship platform
- Parent portal
- Student portal
- Teacher portal
- Dashboard and analytics endpoints
- PDF and Excel report generation
- Redis caching
- Auto-generated OpenAPI docs at `/api/docs`
- Docker Compose deployment
- Kubernetes manifests
- Heroku deployment config
- Flutter mobile companion app
- Seed scripts for demo data (phases 1–6)
- Quickstart script for DB init and admin creation

### Tech Stack
- FastAPI 0.115.0, Python 3.11
- PostgreSQL 15 + SQLAlchemy 2.0
- Alembic, JWT, bcrypt, Redis
- Docker, Kubernetes, Heroku

---

[Unreleased]: https://github.com/eodenyire/openemis/compare/v4.0.0...HEAD
[v4.0.0]: https://github.com/eodenyire/openemis/releases/tag/v4.0.0
[v3.0.0]: https://github.com/eodenyire/openemis/releases/tag/v3.0.0
[v2.0.0]: https://github.com/eodenyire/openemis/releases/tag/v2.0.0
[v1.0.0]: https://github.com/eodenyire/openemis/releases/tag/v1.0.0
