# API Reference

This document covers the REST APIs for v1 and v2. Both use FastAPI with auto-generated OpenAPI docs.

- v1 interactive docs: `http://localhost:8000/api/docs`
- v2 interactive docs: `http://localhost:8001/api/docs`

---

## Authentication

Both versions use JWT Bearer tokens.

### Login

```
POST /api/v1/auth/login      (v1)
POST /api/v2/auth/login      (v2)
```

Request body:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include in all subsequent requests:
```
Authorization: Bearer <access_token>
```

Token expiry: 30 minutes (v1), 60 minutes (v2). Re-authenticate to get a new token.

---

## v1 API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Authenticate and get JWT token |
| POST | `/auth/logout` | Invalidate session |
| GET | `/auth/me` | Get current user profile |
| POST | `/auth/change-password` | Change password |

### Users

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users/` | List all users (admin only) |
| POST | `/users/` | Create user |
| GET | `/users/{id}` | Get user by ID |
| PUT | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |

### Students

| Method | Path | Description |
|--------|------|-------------|
| GET | `/students/` | List students (paginated) |
| POST | `/students/` | Create student |
| GET | `/students/{id}` | Get student by ID |
| PUT | `/students/{id}` | Update student |
| DELETE | `/students/{id}` | Delete student |
| GET | `/students/{id}/attendance` | Student attendance history |
| GET | `/students/{id}/results` | Student exam results |
| GET | `/students/{id}/fees` | Student fee records |

### Faculty / Teachers

| Method | Path | Description |
|--------|------|-------------|
| GET | `/people/faculty/` | List faculty members |
| POST | `/people/faculty/` | Create faculty member |
| GET | `/people/faculty/{id}` | Get faculty by ID |
| PUT | `/people/faculty/{id}` | Update faculty |
| DELETE | `/people/faculty/{id}` | Delete faculty |

### Courses & Subjects

| Method | Path | Description |
|--------|------|-------------|
| GET | `/core/courses/` | List courses |
| POST | `/core/courses/` | Create course |
| GET | `/core/courses/{id}` | Get course |
| PUT | `/core/courses/{id}` | Update course |
| GET | `/core/subjects/` | List subjects |
| POST | `/core/subjects/` | Create subject |

### Admissions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admissions/` | List applications |
| POST | `/admissions/` | Submit application |
| GET | `/admissions/{id}` | Get application |
| PUT | `/admissions/{id}/approve` | Approve application |
| PUT | `/admissions/{id}/reject` | Reject application |

### Attendance

| Method | Path | Description |
|--------|------|-------------|
| GET | `/attendance/` | List attendance records |
| POST | `/attendance/` | Record attendance |
| GET | `/attendance/summary` | Attendance summary report |
| GET | `/attendance/student/{id}` | Student attendance |

### Exams

| Method | Path | Description |
|--------|------|-------------|
| GET | `/exam/` | List exams |
| POST | `/exam/` | Create exam |
| GET | `/exam/{id}` | Get exam |
| POST | `/exam/{id}/marks` | Submit marks |
| GET | `/exam/{id}/results` | Get results |
| GET | `/exam/grades/` | Grade configuration |

### Fees

| Method | Path | Description |
|--------|------|-------------|
| GET | `/fees/` | List fee records |
| POST | `/fees/` | Create fee record |
| GET | `/fees/structure/` | Fee structure |
| POST | `/fees/structure/` | Create fee structure |
| GET | `/fees/invoices/` | List invoices |
| POST | `/fees/invoices/` | Generate invoice |

### Payments (M-Pesa)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/payments/mpesa/stk-push` | Initiate M-Pesa STK push |
| POST | `/payments/mpesa/callback` | M-Pesa payment callback |
| GET | `/payments/` | List payment records |

### Library

| Method | Path | Description |
|--------|------|-------------|
| GET | `/library/books/` | List books |
| POST | `/library/books/` | Add book |
| GET | `/library/books/{id}` | Get book |
| POST | `/library/issue/` | Issue book to student |
| POST | `/library/return/` | Return book |
| GET | `/library/overdue/` | List overdue books |

### Hostel

| Method | Path | Description |
|--------|------|-------------|
| GET | `/hostel/rooms/` | List rooms |
| POST | `/hostel/rooms/` | Create room |
| POST | `/hostel/allocate/` | Allocate student to room |
| GET | `/hostel/allocations/` | List allocations |

### Transportation

| Method | Path | Description |
|--------|------|-------------|
| GET | `/transport/routes/` | List routes |
| POST | `/transport/routes/` | Create route |
| GET | `/transport/vehicles/` | List vehicles |
| POST | `/transport/assign/` | Assign student to route |

### HR

| Method | Path | Description |
|--------|------|-------------|
| GET | `/hr/staff/` | List staff |
| POST | `/hr/staff/` | Create staff record |
| GET | `/hr/leave/` | List leave requests |
| POST | `/hr/leave/` | Submit leave request |
| GET | `/hr/payroll/` | Payroll records |

### Analytics & Dashboard

| Method | Path | Description |
|--------|------|-------------|
| GET | `/analytics/overview` | System-wide statistics |
| GET | `/analytics/enrollment` | Enrollment trends |
| GET | `/analytics/attendance` | Attendance analytics |
| GET | `/analytics/performance` | Academic performance |
| GET | `/dashboard/` | Dashboard summary |

### CBC (Competency-Based Curriculum)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/cbc/strands/` | List CBC strands |
| GET | `/cbc/competencies/` | List competencies |
| POST | `/cbc/assessments/` | Record CBC assessment |
| GET | `/cbc/reports/{student_id}` | CBC progress report |

### DigiGuide

| Method | Path | Description |
|--------|------|-------------|
| GET | `/digiguide/careers/` | List career paths |
| GET | `/digiguide/predict/{student_id}` | Predict KCSE performance |
| GET | `/digiguide/kuccps/` | KUCCPS course requirements |
| POST | `/digiguide/guidance/` | Record career guidance session |

### Mentorship

| Method | Path | Description |
|--------|------|-------------|
| GET | `/mentorship/mentors/` | List mentors |
| POST | `/mentorship/mentors/` | Register as mentor |
| POST | `/mentorship/sessions/` | Schedule session |
| GET | `/mentorship/forums/` | List group forums |

### Reports

| Method | Path | Description |
|--------|------|-------------|
| GET | `/reports/students` | Student report (PDF/Excel) |
| GET | `/reports/attendance` | Attendance report |
| GET | `/reports/exams` | Exam results report |
| GET | `/reports/fees` | Fee collection report |
| GET | `/reports/hr` | HR report |

### SMS (Africa's Talking)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/sms/send` | Send SMS to individual |
| POST | `/sms/bulk` | Send bulk SMS |

### NEMIS / KNEC / TPAD (Kenya-specific)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/nemis/students/` | NEMIS student data sync |
| POST | `/nemis/submit/` | Submit to NEMIS |
| GET | `/knec/results/` | KNEC exam results |
| GET | `/tpad/appraisals/` | TPAD teacher appraisals |

---

## v2 API Endpoints

Base URL: `http://localhost:8001/api/v2`

v2 shares the same authentication pattern as v1. The endpoint set is a refined subset focused on the core educational domain.

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Authenticate and get JWT |
| GET | `/auth/me` | Current user profile |

### Core (Students, Faculty, Courses)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/core/students/` | List students |
| POST | `/core/students/` | Create student |
| GET | `/core/students/{id}` | Get student |
| PUT | `/core/students/{id}` | Update student |
| DELETE | `/core/students/{id}` | Delete student |
| GET | `/core/faculty/` | List faculty |
| POST | `/core/faculty/` | Create faculty |
| GET | `/core/courses/` | List courses |
| POST | `/core/courses/` | Create course |
| GET | `/core/subjects/` | List subjects |
| GET | `/core/academic-years/` | List academic years |

### Admissions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admission/` | List applications |
| POST | `/admission/` | Submit application |
| GET | `/admission/{id}` | Get application |
| PUT | `/admission/{id}` | Update application |

### Attendance

| Method | Path | Description |
|--------|------|-------------|
| GET | `/attendance/` | List records |
| POST | `/attendance/` | Record attendance |
| GET | `/attendance/summary` | Summary report |

### Exams

| Method | Path | Description |
|--------|------|-------------|
| GET | `/exam/` | List exams |
| POST | `/exam/` | Create exam |
| POST | `/exam/{id}/marks` | Submit marks |
| GET | `/exam/{id}/results` | Get results |

### Fees

| Method | Path | Description |
|--------|------|-------------|
| GET | `/fees/` | List fee records |
| POST | `/fees/` | Create fee record |
| GET | `/fees/invoices/` | List invoices |

### Library

| Method | Path | Description |
|--------|------|-------------|
| GET | `/library/books/` | List books |
| POST | `/library/books/` | Add book |
| POST | `/library/issue/` | Issue book |
| POST | `/library/return/` | Return book |

### Timetable

| Method | Path | Description |
|--------|------|-------------|
| GET | `/timetable/` | List timetable entries |
| POST | `/timetable/` | Create timetable entry |
| GET | `/timetable/class/{id}` | Class timetable |

### LMS

| Method | Path | Description |
|--------|------|-------------|
| GET | `/lms/courses/` | List LMS courses |
| POST | `/lms/courses/` | Create LMS course |
| GET | `/lms/courses/{id}/materials` | Course materials |
| POST | `/lms/enroll/` | Enroll student |

### Mentorship

| Method | Path | Description |
|--------|------|-------------|
| GET | `/mentorship/mentors/` | List mentors |
| POST | `/mentorship/sessions/` | Schedule session |
| GET | `/mentorship/forums/` | Group forums |

### DigiGuide

| Method | Path | Description |
|--------|------|-------------|
| GET | `/digiguide/careers/` | Career paths |
| GET | `/digiguide/predict/{id}` | Performance prediction |

### Other Modules

| Module | Base Path |
|--------|-----------|
| Activities | `/activities/` |
| Alumni | `/alumni/` |
| Events | `/events/` |
| Facilities | `/facilities/` |
| Health | `/health/` |
| Hostel | `/hostel/` |
| Notice Board | `/noticeboard/` |
| Scholarships | `/scholarships/` |
| Transport | `/transport/` |

---

## Common Response Formats

### Success (list)
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20
}
```

### Success (single)
```json
{
  "id": 1,
  "field": "value",
  ...
}
```

### Error
```json
{
  "detail": "Student not found"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Pagination

List endpoints support pagination via query parameters:

```
GET /api/v1/students/?page=1&size=20
GET /api/v1/students/?skip=0&limit=20
```

## Filtering

Most list endpoints support filtering:

```
GET /api/v1/students/?class_id=5&academic_year=2024
GET /api/v1/attendance/?date=2024-01-15&class_id=3
GET /api/v1/exam/?subject_id=2&term=1
```

## Odoo / v3 API

v3 uses the Odoo JSON-RPC API. See the [Odoo External API documentation](https://www.odoo.com/documentation/18.0/developer/reference/external_api.html) for details. The Odoo web client handles all UI interactions natively.
