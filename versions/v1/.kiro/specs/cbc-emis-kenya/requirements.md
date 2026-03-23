# Requirements Document

## Introduction

CBC EMIS Kenya is a multi-tenant, CBC-compliant Educational Management Information System for Kenyan
schools covering Pre-Primary through Grade 12/13. It extends the existing FastAPI + PostgreSQL backend
with multi-tenancy, CBC curriculum models, Kenya-specific integrations (NEMIS, M-Pesa, Africa's Talking),
a 15-role RBAC system, and a modern Next.js 14 frontend. The system is delivered in three phases:
Phase 1 (CBC models + NEMIS UPI + M-Pesa basics), Phase 2 (multi-tenancy + report cards + SMS),
Phase 3 (analytics + mobile + KNEC).

---

## Glossary

- **System**: The CBC EMIS Kenya platform as a whole
- **Auth_Service**: The authentication and authorisation microservice
- **Student_Service**: The student lifecycle microservice
- **Academic_Service**: The CBC curriculum, timetable, and attendance microservice
- **Assessment_Service**: The CAT, exam, and report card microservice
- **Finance_Service**: The fees, invoices, and payments microservice
- **HR_Service**: The staff profiles, leave, and payroll microservice
- **Communication_Service**: The SMS, email, and in-app notification microservice
- **Analytics_Service**: The BI, enrollment trends, and at-risk detection microservice
- **Tenant**: A school or school network registered on the platform, identified by a unique slug
- **GradeLevel**: A CBC grade band (PP1, PP2, Grade 1–12) belonging to a school
- **ClassStream**: A named section within a GradeLevel (e.g. "7A", "7B")
- **LearningArea**: A CBC subject offered at a GradeLevel (e.g. Mathematics, English)
- **Strand**: A thematic grouping within a LearningArea
- **SubStrand**: A specific topic within a Strand
- **CompetencyIndicator**: A measurable learning outcome mapped to a CBC competency
- **PerformanceLevel**: One of EE (Exceeds Expectation), ME (Meets Expectation), AE (Approaches Expectation), BE (Below Expectation)
- **ReportCard**: A per-student, per-term CBC assessment summary document
- **NEMIS**: National Education Management Information System — Kenya MoE student registry
- **UPI**: Unique Pupil Identifier assigned by NEMIS
- **KNEC**: Kenya National Examinations Council
- **STK_Push**: Safaricom M-Pesa Lipa Na M-Pesa online payment initiation
- **TPAD**: Teacher Performance Appraisal and Development — Kenya TSC framework
- **TSC**: Teachers Service Commission — Kenya
- **Celery_Worker**: Async task worker for background jobs (SMS, PDF, bulk operations)
- **TenantQueryMixin**: SQLAlchemy mixin that injects tenant_id filter on every query


---

## Requirements

### Requirement 1: Multi-Tenancy and Tenant Isolation

**User Story:** As a school network administrator, I want each school to have its own isolated data
space, so that student records, fees, and assessments from one school are never visible to another.

#### Acceptance Criteria

1. THE System SHALL store every data record with a non-null `tenant_id` foreign key referencing the `tenants` table.
2. WHEN an authenticated API request is received, THE Auth_Service SHALL inject the caller's `tenant_id` into the request context before any database query executes.
3. WHILE processing any database query, THE TenantQueryMixin SHALL append a `WHERE tenant_id = :current_tenant_id` filter to every query that targets a tenant-scoped table.
4. IF a request attempts to read or write a record whose `tenant_id` does not match the caller's `tenant_id`, THEN THE System SHALL return HTTP 403 Forbidden.
5. THE System SHALL support a `TenantGroup` entity that groups multiple `Tenant` records under a single billing and administrative umbrella.
6. WHEN a new tenant is created, THE System SHALL provision a default set of CBC grade levels (PP1, PP2, Grade 1–12) and the 15 system roles for that tenant.

---

### Requirement 2: Authentication and 15-Role RBAC

**User Story:** As a system administrator, I want granular role-based access control with 15 distinct
roles, so that each user type can only access the data and actions appropriate to their function.

#### Acceptance Criteria

1. THE Auth_Service SHALL support exactly 15 named roles: Super Admin, School Admin, Academic Director, Teacher, Student, Parent/Guardian, Finance Officer, Registrar, Librarian, Transport Manager, HR Manager, Nurse/Health Officer, Hostel Manager, Security/Gate Officer, Government Dashboard.
2. WHEN a user logs in with valid credentials and a valid `tenant_slug`, THE Auth_Service SHALL return a JWT access token (expiry 15 minutes) and a refresh token (expiry 7 days) containing the user's `tenant_id`, roles, and resolved permission strings.
3. WHEN a JWT access token expires, THE Auth_Service SHALL reject the request with HTTP 401 and require the client to use the refresh token endpoint.
4. WHEN a user logs out, THE Auth_Service SHALL add the token's JTI to a Redis blacklist so that the token is rejected on all subsequent requests before its natural expiry.
5. THE System SHALL store permissions in a `role_permissions` table using the pattern `resource:action:scope` (e.g. `students:read:class`).
6. WHEN an API endpoint is called, THE Auth_Service SHALL verify that the caller's JWT contains the required permission string for that endpoint before allowing the request to proceed.
7. IF the caller's JWT does not contain the required permission, THEN THE Auth_Service SHALL return HTTP 403 Forbidden with a descriptive error message.
8. WHERE a user holds the Super Admin role, THE Auth_Service SHALL bypass tenant-scoped permission checks and allow cross-tenant operations.

---

### Requirement 3: CBC Curriculum Structure

**User Story:** As an academic director, I want the system to model the full CBC curriculum hierarchy
(GradeLevel → LearningArea → Strand → SubStrand → CompetencyIndicator), so that assessments and
report cards are aligned to the official Kenya curriculum framework.

#### Acceptance Criteria

1. THE Academic_Service SHALL maintain GradeLevel records for PP1, PP2, and Grade 1 through Grade 12, each tagged with a band (pre_primary, lower_primary, upper_primary, jss, sss).
2. THE Academic_Service SHALL associate LearningArea records with a specific GradeLevel, including weekly lesson count and whether the area is compulsory.
3. THE Academic_Service SHALL support a four-level curriculum hierarchy: LearningArea → Strand → SubStrand → CompetencyIndicator.
4. WHEN a CompetencyIndicator is created, THE Academic_Service SHALL require it to reference both a CBC competency (CC1–CC8) and a learning outcome.
5. THE Academic_Service SHALL expose read-only endpoints for the full CBC curriculum tree, filterable by GradeLevel.
6. WHEN a ClassStream is created, THE Academic_Service SHALL require it to reference a GradeLevel and a class teacher, and SHALL enforce a maximum capacity.

---

### Requirement 4: Student Lifecycle Management

**User Story:** As a registrar, I want to manage the full student lifecycle from admission through
graduation or transfer, so that every student's record is complete, accurate, and NEMIS-compliant.

#### Acceptance Criteria

1. THE Student_Service SHALL store a `nemis_upi` field on every student record, which may be null until NEMIS synchronisation is completed.
2. WHEN a student record is created or updated with sufficient identity data (name, date of birth, gender), THE Student_Service SHALL expose a `POST /students/{id}/nemis-sync` endpoint that submits the student to the NEMIS API and stores the returned UPI.
3. IF the NEMIS API is unavailable during a sync attempt, THEN THE Student_Service SHALL save the student without a UPI and enqueue a Celery retry task that retries every 30 minutes for up to 24 hours.
4. WHEN a student transfer is initiated, THE Student_Service SHALL set the student's current enrollment status to "transferred", create a new enrollment record at the target school, and record the transfer reason and effective date.
5. THE Student_Service SHALL support bulk student import via CSV/Excel upload, returning a result summary with counts of created, updated, and failed records.
6. WHEN a student's enrollment status changes, THE Student_Service SHALL create an audit log entry recording the previous status, new status, actor, and timestamp.
7. THE Student_Service SHALL link students to one or more Parent/Guardian records and expose child-specific data views scoped to the parent's linked children.

---

### Requirement 5: Attendance Tracking

**User Story:** As a teacher, I want to record daily and per-lesson attendance for my class, so that
the school has accurate attendance data and parents are notified when their child's attendance drops.

#### Acceptance Criteria

1. THE Academic_Service SHALL support two attendance session types: `daily` (one per class per day) and `lesson` (one per period per learning area per day).
2. WHEN an attendance session is created for a class stream and date that already has a session of the same type and period, THE Academic_Service SHALL return HTTP 409 Conflict.
3. THE Academic_Service SHALL accept attendance status values of `present`, `absent`, `late`, and `excused` for each student in a session.
4. WHEN computing an attendance percentage for a student, THE Academic_Service SHALL calculate it as (present + late) / total_sessions × 100, rounded to one decimal place.
5. WHEN a student's attendance percentage falls below 75% in any rolling 30-day window, THE Communication_Service SHALL send an SMS notification to the student's registered parent/guardian phone number.
6. THE Academic_Service SHALL maintain a materialized view `attendance_summary` aggregated by student, class stream, session type, and calendar month.
7. WHEN bulk attendance is submitted for a class, THE Academic_Service SHALL record all attendance records atomically — either all succeed or none are persisted.

---

### Requirement 6: CBC Assessment and Report Cards

**User Story:** As a teacher, I want to record competency-based assessment scores and generate
CBC-format report cards, so that students and parents receive meaningful feedback aligned to the
national curriculum.

#### Acceptance Criteria

1. THE Assessment_Service SHALL support assessment types: CAT, end_of_term, project, and observation.
2. WHEN a raw score is submitted for a competency indicator, THE Assessment_Service SHALL convert it to a PerformanceLevel using the rule: score ≥ 75% → EE, 50–74% → ME, 25–49% → AE, < 25% → BE.
3. THE Assessment_Service SHALL store the PerformanceLevel as one of exactly four values: EE, ME, AE, or BE.
4. WHEN a report card is generated for a student and term, THE Assessment_Service SHALL compute a weighted average score per LearningArea across all closed assessments in that term, then convert the average to a PerformanceLevel.
5. WHEN a report card is generated, THE Assessment_Service SHALL create a ReportCard record with status `draft` and link all contributing CompetencyScore records to it.
6. WHEN a report card is published, THE Assessment_Service SHALL set its status to `published`, record the `published_at` timestamp, and trigger a notification to the student's parent/guardian.
7. THE Assessment_Service SHALL generate a PDF version of each published report card using a school-branded HTML/CSS template and store the PDF URL on the ReportCard record.
8. IF a report card PDF generation fails, THEN THE Assessment_Service SHALL log the error, preserve the draft ReportCard record, and return HTTP 500 with a descriptive error.
9. THE Assessment_Service SHALL expose a bulk report card generation endpoint that accepts a `class_stream_id` and `term_id` and returns a Celery `task_id` for async processing.

---

### Requirement 7: Fee Management and M-Pesa Integration

**User Story:** As a finance officer, I want to manage fee structures, generate invoices, and accept
M-Pesa payments, so that fee collection is efficient, traceable, and reconciled automatically.

#### Acceptance Criteria

1. THE Finance_Service SHALL support fee structures with multiple line items, each with a name, amount, and optional grade-level scope.
2. WHEN bulk invoice generation is triggered for a term, THE Finance_Service SHALL create exactly one invoice per active enrolled student in the target scope, with line items matching the applicable fee structure.
3. WHEN an M-Pesa STK Push is initiated, THE Finance_Service SHALL validate that the requested amount does not exceed the invoice's outstanding balance before calling the Safaricom Daraja API.
4. WHEN the Safaricom Daraja API returns `ResponseCode: "0"` for an STK Push, THE Finance_Service SHALL store the `CheckoutRequestID` and set the `mpesa_stk_requests` record status to `pending`.
5. WHEN the M-Pesa callback is received with `ResultCode: 0`, THE Finance_Service SHALL update the `mpesa_stk_requests` status to `success`, create a `fee_payments` record, increment the invoice `paid_amount`, and enqueue an SMS receipt notification.
6. IF the M-Pesa callback is received with a non-zero `ResultCode`, THEN THE Finance_Service SHALL update the `mpesa_stk_requests` status to `failed` and enqueue an SMS failure notification.
7. THE Finance_Service SHALL ensure idempotency on M-Pesa callbacks by checking for an existing `mpesa_receipt_no` before processing a callback, returning HTTP 200 without duplicate payment creation if already processed.
8. THE Finance_Service SHALL expose a fee collection report endpoint returning total invoiced, total collected, and outstanding balance per term, filterable by grade level.
9. WHEN a fee invoice is created or updated, THE Finance_Service SHALL ensure the invoice total equals the sum of all its line item amounts.


---

### Requirement 8: HR Module

**User Story:** As an HR manager, I want to manage staff profiles, TSC numbers, leave requests, TPAD
appraisals, and payroll, so that the school's human resources are administered within the same system.

#### Acceptance Criteria

1. THE HR_Service SHALL store a staff profile for every employee, including TSC number, qualifications, employment type, and department.
2. WHEN a leave request is submitted by a staff member, THE HR_Service SHALL validate that the requested days do not exceed the staff member's remaining leave balance for the leave type.
3. WHEN a leave request is approved by an authorised approver, THE HR_Service SHALL deduct the approved days from the staff member's leave balance and update the request status to `approved`.
4. THE HR_Service SHALL support TPAD appraisal records per teacher per term, with criteria scores and an overall rating.
5. WHEN a payroll run is executed for a period, THE HR_Service SHALL compute gross pay, apply all configured deductions and allowances, and persist a payroll entry per staff member.
6. IF a payroll run is executed for a period that already has a completed payroll run, THEN THE HR_Service SHALL return HTTP 409 Conflict to prevent duplicate payroll processing.

---

### Requirement 9: Communication and Notifications

**User Story:** As a school administrator, I want to send SMS and email notifications to parents,
students, and staff, so that the school community is informed of important events and updates.

#### Acceptance Criteria

1. THE Communication_Service SHALL support notification channels: SMS (via Africa's Talking), email (via SMTP/SendGrid), and in-app (via WebSocket).
2. WHEN an SMS notification is dispatched, THE Communication_Service SHALL render the message using a Jinja2 template stored in the `notification_templates` table and send it via the Africa's Talking API.
3. IF the Africa's Talking API call fails, THEN THE Communication_Service SHALL retry the SMS delivery using exponential backoff with a maximum of 3 attempts, with delays of 60, 120, and 240 seconds.
4. THE Communication_Service SHALL log every notification dispatch attempt to the `notification_logs` table, recording channel, recipient, template code, status, and timestamp.
5. WHEN a notice board post is created, THE Communication_Service SHALL make it visible to all users with the appropriate role scope within the tenant.
6. THE Communication_Service SHALL support bilingual notification templates in English and Kiswahili, selectable per tenant.

---

### Requirement 10: Timetable Scheduling

**User Story:** As an academic director, I want the system to generate a conflict-free weekly
timetable for all class streams, so that no teacher or classroom is double-booked.

#### Acceptance Criteria

1. WHEN timetable generation is triggered for a set of class streams and a term, THE Academic_Service SHALL return a Celery `task_id` immediately and run the constraint solver asynchronously.
2. THE Academic_Service SHALL enforce hard timetable constraints: a teacher cannot be assigned to two different class streams in the same day-period slot, a classroom cannot host two classes in the same slot, and a class stream cannot have two subjects in the same slot.
3. WHEN the timetable generator cannot produce a conflict-free schedule with the given constraints, THE Academic_Service SHALL return HTTP 422 with a description of the conflicting constraints.
4. WHEN a timetable entry is manually edited, THE Academic_Service SHALL validate the edit against all hard constraints before persisting it, returning HTTP 409 if a conflict is detected.
5. THE Academic_Service SHALL ensure that every class stream's generated timetable contains exactly the required number of weekly lessons per LearningArea as configured in the curriculum.

---

### Requirement 11: Analytics and Government Reporting

**User Story:** As a government dashboard user, I want to view aggregated enrollment, attendance, and
performance data across schools in my county, so that I can monitor education outcomes and allocate
resources effectively.

#### Acceptance Criteria

1. THE Analytics_Service SHALL compute enrollment trends per grade level per academic year, aggregated at tenant, county, and national levels.
2. THE Analytics_Service SHALL compute performance analytics per learning area per term, showing distribution of EE/ME/AE/BE levels across a class stream or grade level.
3. WHEN a student's attendance falls below 75% or their assessment results show BE in three or more learning areas in a term, THE Analytics_Service SHALL create an `at_risk_flags` record for that student.
4. THE Analytics_Service SHALL expose a government report endpoint that returns aggregate statistics (enrollment counts, attendance rates, performance distributions) for a given county and academic year, accessible only to users with the Government Dashboard role.
5. THE Analytics_Service SHALL refresh analytics snapshots on a scheduled basis (at minimum daily) using Celery Beat.

---

### Requirement 12: Support Services (Library, Hostel, Transport, Health)

**User Story:** As a support services manager, I want to manage library borrowing, hostel allocations,
transport routes, and student health records within the same system, so that all school operations
are centralised.

#### Acceptance Criteria

1. THE System SHALL track library media borrowing with borrow date, due date, return date, and overdue fine calculation.
2. THE System SHALL manage hostel room allocations, linking students to rooms for a given academic year, and preventing over-allocation beyond room capacity.
3. THE System SHALL manage transport routes with stops, assigned vehicles, and student-route assignments.
4. THE System SHALL store student health records including medical conditions, sick bay visits, immunisation records, and health alerts.
5. WHEN a library item is overdue, THE System SHALL calculate the overdue fine based on the number of days past the due date and a configurable daily fine rate.

---

### Requirement 13: KNEC Exam Registration Integration

**User Story:** As a registrar, I want to register eligible students for KNEC national examinations
directly from the system, so that exam registration is accurate and traceable.

#### Acceptance Criteria

1. WHEN KNEC exam registration is submitted for a cohort of students, THE Student_Service SHALL send the school's KNEC code and candidate list to the KNEC API and store the returned index numbers on each student record.
2. IF the KNEC API is unavailable, THEN THE Student_Service SHALL queue the registration for async retry and notify the registrar of the pending status.
3. THE Student_Service SHALL prevent duplicate KNEC registrations for the same student and exam year by checking for an existing `knec_registrations` record before submitting.

---

### Requirement 14: Academic Calendar

**User Story:** As a school administrator, I want to define the academic calendar with term dates,
holidays, and events, so that all scheduling and reporting is aligned to the school year.

#### Acceptance Criteria

1. THE Academic_Service SHALL support academic year records with a start date and end date.
2. THE Academic_Service SHALL support academic term records (up to three per year) with term start date, end date, and term number.
3. THE Academic_Service SHALL support academic calendar events (e.g. open days, sports days) and school holidays, each linked to an academic year.
4. WHEN a timetable or assessment is scheduled outside the active academic term's date range, THE Academic_Service SHALL return a validation error.

---

### Requirement 15: Data Migration from Existing System

**User Story:** As a system administrator, I want to migrate the existing single-school data to the
new multi-tenant CBC schema without data loss, so that the school can continue operating without
interruption.

#### Acceptance Criteria

1. THE System SHALL provide Alembic migration scripts that add new CBC EMIS tables alongside existing tables without dropping or modifying existing data.
2. WHEN Phase 1 migration scripts are applied, THE System SHALL add a nullable `tenant_id` column to all existing tenant-scoped tables without breaking existing API functionality.
3. THE System SHALL provide a data migration script that creates a default tenant record and assigns all existing users, students, and teachers to that tenant.
4. THE System SHALL map the existing 5 user roles (admin, teacher, student, parent, staff) to their corresponding new RBAC roles during migration.
5. THE System SHALL map existing `Course` and `Batch` records to `GradeLevel` and `ClassStream` records using CBC band detection from the course name.
6. WHEN the migration is complete, THE System SHALL validate that every existing record has a non-null `tenant_id` and that no data has been lost by comparing record counts before and after migration.

---

### Requirement 16: Non-Functional Requirements — Performance

**User Story:** As a school with up to 2,000 students, I want the system to respond quickly under
normal load, so that teachers and administrators are not blocked waiting for the system.

#### Acceptance Criteria

1. WHEN a list endpoint (students, attendance, assessments) is called with standard pagination, THE System SHALL respond within 500ms at the 95th percentile under a load of 500 concurrent users.
2. WHEN a report card is generated for a single student, THE Assessment_Service SHALL complete the generation within 2 seconds.
3. WHEN bulk report card generation is triggered for a class stream of up to 50 students, THE Celery_Worker SHALL complete all report cards within 5 minutes.
4. THE System SHALL cache frequently read, rarely changed data (CBC curriculum tree, role permissions) in Redis with a TTL of at least 1 hour.

---

### Requirement 17: Non-Functional Requirements — Security

**User Story:** As a data protection officer, I want the system to protect student PII and financial
data, so that the school complies with Kenya's Data Protection Act 2019.

#### Acceptance Criteria

1. THE System SHALL encrypt student NEMIS UPIs and phone numbers at rest using PostgreSQL `pgcrypto`.
2. THE System SHALL enforce HTTPS-only communication with TLS 1.2 or higher at the ingress layer.
3. WHEN an M-Pesa callback is received, THE Finance_Service SHALL verify the request originates from a Safaricom IP address before processing it.
4. THE System SHALL log every create, update, and delete operation to the `audit_logs` table, recording the actor's user ID, tenant ID, affected table, record ID, operation type, and timestamp.
5. THE System SHALL apply rate limiting of 5 requests per minute per IP address on authentication endpoints.
6. WHEN a file is uploaded, THE System SHALL scan it for malware before storing it in object storage, rejecting files that fail the scan.

---

### Requirement 18: Non-Functional Requirements — Scalability and Deployment

**User Story:** As a cloud infrastructure engineer, I want the system to scale horizontally and
support both Kubernetes and single-server deployments, so that it can serve schools of all sizes.

#### Acceptance Criteria

1. THE System SHALL be deployable as a Docker Compose stack (api, worker, postgres, redis, minio) for schools with fewer than 2,000 students.
2. THE System SHALL be deployable on Kubernetes with Horizontal Pod Autoscaling enabled for the FastAPI and Celery worker pods.
3. THE System SHALL use stateless FastAPI pods so that any pod can handle any request without shared in-process state.
4. WHEN a Celery task fails after all retries are exhausted, THE Celery_Worker SHALL move the task to a dead-letter queue and alert the system administrator.

