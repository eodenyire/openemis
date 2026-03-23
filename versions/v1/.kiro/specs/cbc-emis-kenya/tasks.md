# CBC EMIS Kenya — Implementation Tasks

> World-class K-12 EMIS for Kenyan CBC schools (PP1 → Grade 12).
> Inspired by PowerSchool, Canvas, Moodle, Blackbaud, Skyward, Edsby, openSIS.
> Built on: FastAPI · PostgreSQL · SQLAlchemy · Next.js 14 · Flutter · Redis · Celery

---

## PHASE 1 — CBC Core + Authentication Foundation
> Goal: Rock-solid auth, 15 roles, CBC curriculum models, and role-based dashboards

### Task 1.1 — Expand Auth to 15 Roles
- [-] Add all 15 roles to `UserRole` enum: `SUPER_ADMIN`, `SCHOOL_ADMIN`, `ACADEMIC_DIRECTOR`, `TEACHER`, `STUDENT`, `PARENT`, `FINANCE_OFFICER`, `REGISTRAR`, `LIBRARIAN`, `TRANSPORT_MANAGER`, `HR_MANAGER`, `NURSE`, `HOSTEL_MANAGER`, `SECURITY_OFFICER`, `GOVERNMENT`
- [~] Create `Permission` model (`resource:action:scope` pattern e.g. `students:read:class`)
- [~] Create `RolePermission` and `UserRole` junction models
- [~] Seed default permissions for all 15 roles
- [~] Update `require_permission()` dependency in `deps.py`
- [~] Update JWT payload to include roles + permissions array
- [~] Add refresh token endpoint with Redis blacklist on logout

### Task 1.2 — CBC Curriculum Models
- [~] Create `CBCGradeLevel` model (PP1, PP2, Grade 1–12) with `level_band` (Pre-Primary, Lower Primary, Upper Primary, Junior Secondary, Senior Secondary)
- [~] Create `LearningArea` model (CBC subject per grade band)
- [~] Create `Strand` model (thematic grouping within LearningArea)
- [~] Create `SubStrand` model (specific topic within Strand)
- [~] Create `CompetencyIndicator` model (measurable outcome, maps to 8 CBC competencies)
- [~] Seed all CBC learning areas, strands, sub-strands for Grade 1–9 (MoE curriculum)
- [~] Add `nemis_upi` field to `Student` model + migration

### Task 1.3 — CBC Assessment Models
- [~] Create `CBCAssessment` model (formative/summative, per student per competency)
- [~] Create `CompetencyScore` model with `PerformanceLevel` enum (EE/ME/AE/BE)
- [~] Create `ReportCard` model (per student, per term, per grade)
- [~] Create `ReportCardLine` model (one per LearningArea per ReportCard)
- [~] Implement `score_to_cbc_level()` utility (maps raw score → EE/ME/AE/BE)
- [~] Add CBC report card PDF generation endpoint (WeasyPrint/ReportLab)

### Task 1.4 — Role-Based Dashboard API
- [~] Create `/api/v1/dashboard/summary` endpoint returning role-specific stats
- [~] Super Admin: total schools, students, teachers, system health
- [~] School Admin: enrollment, attendance today, fee collection, upcoming exams
- [~] Teacher: my classes today, assignments to grade, attendance pending
- [~] Student: today's timetable, assignments due, recent grades
- [~] Parent: child attendance, fees due, recent exam results
- [~] Finance Officer: today's payments, outstanding fees, expense summary
- [~] Registrar: new applications, pending admissions, transfers


---

## PHASE 2 — Multi-Tenancy + Student Lifecycle + Finance
> Goal: Multi-school SaaS, full student lifecycle, M-Pesa payments

### Task 2.1 — Multi-Tenancy
- [~] Create `Tenant` model (school) with `slug`, `name`, `county`, `sub_county`, `school_type`, `subscription_plan`
- [~] Create `TenantGroup` model (school network / county cluster)
- [~] Add `tenant_id` column to all tenant-scoped models via Alembic migration
- [~] Implement `TenantMiddleware` — injects `tenant_id` from JWT into request context
- [~] Implement `TenantQueryMixin` — auto-appends `WHERE tenant_id = ?` to all queries
- [~] Add tenant provisioning endpoint (creates default CBC grades + 15 roles on signup)
- [~] Enforce HTTP 403 on cross-tenant data access

### Task 2.2 — Student Lifecycle (PowerSchool-inspired)
- [~] Admission workflow: Application → Interview → Approval → Enrollment (state machine)
- [~] Student transfer management (inter-school, with NEMIS UPI tracking)
- [~] Student promotion engine (end-of-year bulk promotion PP1→PP2→Grade1…)
- [~] Alumni tracking (graduated students, contact info, career updates)
- [~] Student ID card generation (PDF with photo, QR code, school logo)
- [~] Guardian/Parent linking with relationship types
- [~] Medical records on student profile (allergies, blood group, vaccinations)

### Task 2.3 — M-Pesa STK Push Integration
- [~] Create `MpesaTransaction` model (checkout_request_id, amount, phone, status, callback_data)
- [~] Implement Daraja API service (`initiate_stk_push()`, `query_transaction_status()`)
- [~] Create `/api/v1/payments/mpesa/initiate` endpoint
- [~] Create `/api/v1/payments/mpesa/callback` webhook endpoint
- [~] Idempotency: reject duplicate `checkout_request_id` on callback
- [~] Auto-update `FeePayment` and `StudentFeeInvoice` on successful callback
- [~] Fee receipt generation (PDF) on payment confirmation

### Task 2.4 — Finance Module (Blackbaud-inspired)
- [~] Fee structure builder (per grade, per term, with line items)
- [~] Bulk invoice generation (generate invoices for all students in a grade)
- [~] Payment reconciliation report
- [~] Expense tracking (school operational expenses)
- [~] Payroll integration (link to HR salary records)
- [~] Financial reports: income statement, fee collection summary, outstanding balances
- [~] Bursary/scholarship management (partial fee waivers)

---

## PHASE 3 — Academic Management + LMS
> Goal: Timetable, lesson planning, assignments, digital classroom (Canvas/Moodle-inspired)

### Task 3.1 — Timetable Engine
- [~] Create `TimetableSlot` model (day, period, class, subject, teacher, room)
- [~] Constraint solver: no teacher double-booking, no room double-booking
- [~] Auto-generate timetable from constraints (greedy algorithm)
- [~] Export timetable to PDF per class / per teacher
- [~] Academic calendar management (term dates, holidays, events)

### Task 3.2 — Lesson Planning (Teacher Portal)
- [~] Create `LessonPlan` model (linked to SubStrand, date, objectives, resources, activities)
- [~] Lesson plan approval workflow (Teacher → Academic Director)
- [~] Teaching resource library (upload PDFs, videos, links)
- [~] Scheme of work generator (term-long plan per LearningArea)

### Task 3.3 — LMS — Digital Classroom (Canvas-inspired)
- [~] Create `ClassRoom` (virtual) model with enrolled students
- [~] Assignment submission portal (file upload, text submission)
- [~] Online quiz engine (MCQ, short answer, true/false)
- [~] Discussion forums per class
- [~] Recorded lesson links (YouTube/Vimeo embed or file upload)
- [~] Student progress tracker per LearningArea

### Task 3.4 — Attendance System (Enhanced)
- [~] QR code attendance (teacher scans student QR → marks present)
- [~] Bulk attendance marking (mark all present, then flag absences)
- [~] Attendance alerts: auto-flag students below 75% attendance
- [~] Parent notification on absence (SMS via Africa's Talking)
- [~] Attendance analytics per class, per student, per term

---

## PHASE 4 — HR, Payroll + Staff Management
> Goal: Full HR module (Skyward-inspired), TPAD appraisal, payroll

### Task 4.1 — Staff Profiles + Contracts
- [~] Create `StaffProfile` model (TSC number, qualification, specialization, employment type)
- [~] Contract management (permanent, contract, intern, volunteer)
- [~] Document management (certificates, ID, KRA PIN, NSSF, NHIF)
- [~] Staff directory with search and filter

### Task 4.2 — Leave Management
- [~] Create `LeaveType` model (annual, sick, maternity, paternity, compassionate)
- [~] Create `LeaveRequest` model with approval workflow (Staff → HOD → Principal)
- [~] Leave balance tracking per staff per year
- [~] Leave calendar (visual view of who is on leave)

### Task 4.3 — TPAD Appraisal (Kenya TSC)
- [~] Create `TPADAppraisal` model (term, self-assessment, HOD assessment, score)
- [~] TPAD scoring rubric (Teaching, Professional Development, Participation, Conduct)
- [~] Appraisal report generation per teacher per term
- [~] Performance trend analytics per teacher

### Task 4.4 — Payroll
- [~] Create `PayrollPeriod` and `PayrollEntry` models
- [~] Salary structure (basic, house allowance, transport, medical)
- [~] Statutory deductions (PAYE, NSSF, NHIF, HELB)
- [~] Payslip generation (PDF per staff per month)
- [~] Bank transfer file export (CSV for bank bulk payment)

---

## PHASE 5 — Communication + Parent Portal
> Goal: SMS, email, parent portal, announcements (Edsby/Skyward-inspired)

### Task 5.1 — Africa's Talking SMS Integration
- [~] Implement `ATSMSService` (send_sms, send_bulk_sms)
- [~] Create `SMSLog` model (recipient, message, status, cost, timestamp)
- [~] Notification templates with Jinja2 (attendance alert, fee reminder, exam results, report card)
- [~] Bulk SMS campaigns (send to all parents in a grade)
- [~] SMS delivery status webhook

### Task 5.2 — Email Notifications
- [~] SMTP / SendGrid integration
- [~] HTML email templates (fee invoice, report card, admission letter)
- [~] Email queue via Celery (async sending)
- [~] Email delivery tracking

### Task 5.3 — Parent Portal (Skyward-inspired)
- [~] Parent dashboard: child attendance, grades, fees, announcements
- [~] Multi-child support (parent with 3 kids sees all 3)
- [~] Fee payment via M-Pesa directly from parent portal
- [~] Direct messaging: parent ↔ teacher (threaded)
- [~] Push notifications (mobile app)
- [~] School announcements feed

### Task 5.4 — Announcements + Notice Board
- [~] Create `Announcement` model (title, body, target_roles, publish_date, expiry)
- [~] Audience targeting (all school, specific grade, specific role)
- [~] Pin important announcements
- [~] Event calendar (school events, sports days, parent meetings)

---

## PHASE 6 — Support Services
> Goal: Library, Hostel, Transport, Health — fully operational modules

### Task 6.1 — Library System (Enhanced)
- [~] Digital catalogue with ISBN lookup (Open Library API)
- [~] Barcode/QR scanning for book check-out
- [~] Overdue book alerts (SMS to student/parent)
- [~] Library membership management
- [~] Digital resources section (e-books, journals, links)
- [~] Library usage analytics

### Task 6.2 — Hostel / Boarding Management
- [~] Room allocation with capacity management
- [~] Boarding fee integration with Finance module
- [~] Meal management (menu planning, dietary requirements)
- [~] Boarding attendance (evening roll call)
- [~] Discipline log for boarding students
- [~] Parent notification on boarding incidents

### Task 6.3 — Transport Management
- [~] Route management with GPS coordinates per stop
- [~] Vehicle maintenance log
- [~] Driver profiles and license tracking
- [~] Student transport fee integration
- [~] Real-time tracking placeholder (webhook for GPS device integration)
- [~] Morning/afternoon route attendance

### Task 6.4 — Health / Medical Records
- [~] Student medical profile (blood group, allergies, chronic conditions, vaccinations)
- [~] Clinic visit log (nurse visits, treatment, medication dispensed)
- [~] Vaccination schedule and tracking
- [~] Medical alerts on student profile (visible to teacher + nurse)
- [~] Health analytics (common illnesses, absenteeism due to illness)

---

## PHASE 7 — Analytics + AI + Government Dashboard
> Goal: BI dashboards, dropout prediction, NEMIS/KNEC integration, government reporting

### Task 7.1 — Analytics Dashboards
- [~] Enrollment trends (per grade, per term, per year)
- [~] Attendance analytics (school-wide, class-level, student-level)
- [~] Performance analytics (EE/ME/AE/BE distribution per grade per subject)
- [~] Fee collection analytics (collected vs outstanding, payment method breakdown)
- [~] Teacher workload analytics
- [~] Export all reports to Excel/PDF

### Task 7.2 — AI Early Warning System (Edsby-inspired)
- [~] At-risk student flagging (attendance < 75% OR 3+ consecutive fails)
- [~] Dropout risk score (weighted: attendance + grades + fee arrears + discipline)
- [~] Teacher effectiveness score (class average performance trend)
- [~] Automated intervention alerts (notify class teacher + school admin)
- [~] Performance prediction (end-of-term grade forecast)

### Task 7.3 — NEMIS Integration
- [~] NEMIS UPI sync (push new students, pull existing UPIs)
- [~] Bulk enrollment data export (NEMIS-compatible CSV format)
- [~] School statistics report (MoE format: enrollment by gender, grade, special needs)
- [~] NEMIS data validation (flag students without UPI)

### Task 7.4 — KNEC Integration
- [~] KNEC exam registration export (Grade 9 KJSEA, Grade 12 KCSE candidate list)
- [~] Exam centre management
- [~] Results import (KNEC results CSV → system grades)
- [~] Candidate result slips generation

### Task 7.5 — Government Dashboard
- [~] County-level enrollment statistics
- [~] School performance league tables (anonymized)
- [~] CBC compliance tracking per school
- [~] Teacher-student ratio analytics
- [~] Infrastructure reports (classrooms, labs, libraries)
- [~] Read-only access for Ministry of Education users

---

## PHASE 8 — Frontend (Next.js 14 + Flutter)
> Goal: Modern web dashboard + mobile app for all 15 roles

### Task 8.1 — Next.js 14 Web App
- [~] Authentication pages (login, forgot password, 2FA)
- [~] Role-based layout system (sidebar changes per role)
- [~] Super Admin dashboard
- [~] School Admin / Principal dashboard
- [~] Teacher portal (classes, attendance, grades, lesson plans)
- [~] Student portal (timetable, assignments, grades, library)
- [~] Parent portal (child monitoring, fees, messaging)
- [~] Finance dashboard (payments, invoices, payroll)
- [~] HR dashboard (staff, leave, appraisals)
- [~] Analytics dashboard (charts, tables, exports)
- [~] Government dashboard (read-only analytics)

### Task 8.2 — Flutter Mobile App
- [~] Teacher mobile: mark attendance, view timetable, message parents
- [~] Student mobile: view timetable, submit assignments, check grades
- [~] Parent mobile: child monitoring, M-Pesa fee payment, notifications
- [~] Push notifications (FCM)
- [~] Offline mode for attendance marking

---

## PHASE 9 — Infrastructure + DevOps
> Goal: Production-ready deployment, CI/CD, monitoring

### Task 9.1 — Backend Infrastructure
- [~] Redis integration (session cache, Celery broker, token blacklist)
- [~] Celery worker setup (async SMS, email, PDF generation, bulk ops)
- [~] Alembic migrations for all new models
- [~] Database connection pooling (PgBouncer)
- [~] S3/MinIO for file storage (student photos, documents, report cards)
- [~] Elasticsearch for full-text search (students, staff, library)

### Task 9.2 — CI/CD + Testing
- [~] GitHub Actions pipeline (lint → test → build → deploy)
- [~] pytest test suite (unit + integration, target 80% coverage)
- [~] Property-based tests with Hypothesis (CBC score conversion, fee calculations, attendance %)
- [~] Docker Compose for local dev (app + postgres + redis + celery)
- [~] Kubernetes manifests for production (already started in `/kubernetes`)
- [~] Health check endpoints per service

### Task 9.3 — Security + Compliance
- [~] Rate limiting (per IP, per user, per endpoint)
- [~] Audit log (every write operation logged with user + timestamp + diff)
- [~] Data encryption at rest (sensitive fields: medical, financial)
- [~] HTTPS enforcement + HSTS
- [~] GDPR/Kenya Data Protection Act compliance (data export, deletion)
- [~] Penetration testing checklist

---

## IMPLEMENTATION ORDER (Quick Wins First)

| Priority | Task | Impact |
|----------|------|--------|
| 🔴 NOW | 1.1 — 15 Roles + RBAC | Unlocks all role dashboards |
| 🔴 NOW | 1.2 — CBC Curriculum Models | Core of the system |
| 🔴 NOW | 1.3 — CBC Assessment + Report Cards | Key differentiator |
| 🔴 NOW | 1.4 — Role-Based Dashboard API | Every user sees their data |
| 🟠 NEXT | 2.3 — M-Pesa STK Push | Revenue + Kenya-specific |
| 🟠 NEXT | 2.2 — Student Lifecycle | Admissions + transfers |
| 🟠 NEXT | 3.1 — Timetable Engine | Daily school operations |
| 🟡 SOON | 4.x — HR + Payroll | Staff management |
| 🟡 SOON | 5.x — Communications | Parent engagement |
| 🟢 LATER | 7.x — Analytics + AI | Strategic insights |
| 🟢 LATER | 8.x — Next.js + Flutter | Modern frontend |
| 🟢 LATER | 9.x — DevOps | Production hardening |
