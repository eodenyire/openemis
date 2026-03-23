# v3 Module Dependency Map

This document maps every openEMIS Odoo module, its dependencies, and what it provides.

---

## Dependency Levels

### Level 0 — Odoo Platform (built-in, not openEMIS)

These are standard Odoo modules that openEMIS modules depend on:

| Module | Purpose |
|--------|---------|
| `base` | Core Odoo framework |
| `web` | Odoo web client |
| `mail` | Chatter, messaging, activity tracking |
| `hr` | Human resources base |
| `account` | Accounting and invoicing |
| `product` | Products and pricelists |

---

### Level 1 — Foundation (must install first)

| Module | Depends On | Provides |
|--------|-----------|---------|
| `openemis_core` | `base`, `mail` | Students, faculty, courses, subjects, academic years, terms, enrollment. All other openEMIS modules depend on this. |

---

### Level 2 — Core Extensions (depend only on `openemis_core`)

| Module | Depends On | Provides |
|--------|-----------|---------|
| `openemis_admission` | `openemis_core` | Admissions workflow, application forms, enrolment processing |
| `openemis_attendance` | `openemis_core` | Student and faculty daily attendance tracking, absence reports |
| `openemis_assignment` | `openemis_core` | Assignment creation, student submission, teacher grading |
| `openemis_timetable` | `openemis_core` | Class timetable generation, period scheduling, room allocation |
| `openemis_library` | `openemis_core` | Book catalog, issue/return, overdue tracking, CBC categorisation |
| `openemis_hostel` | `openemis_core` | Hostel rooms, student allocation, room management |
| `openemis_transportation` | `openemis_core` | Transport routes, vehicles, student route assignment |
| `openemis_health` | `openemis_core` | Student health records, medical history, clinic visits |
| `openemis_discipline` | `openemis_core` | Discipline incidents, warnings, suspension records |
| `openemis_scholarship` | `openemis_core` | Scholarship programs, applications, awards |
| `openemis_alumni` | `openemis_core` | Alumni profiles, graduation records, alumni network |
| `openemis_notice_board` | `openemis_core` | Announcements, notices, bulletin board |
| `openemis_event` | `openemis_core` | School events, scheduling, registration |
| `openemis_activity` | `openemis_core` | Extra-curricular activities, clubs, participation |
| `openemis_cafeteria` | `openemis_core` | Cafeteria menu, orders, meal tracking |
| `openemis_facility` | `openemis_core` | School facilities, booking, maintenance |
| `openemis_inventory` | `openemis_core` | School inventory, stock management |
| `openemis_classroom` | `openemis_core` | Classroom management, seating, resources |
| `openemis_achievement` | `openemis_core` | Student achievements, awards, certificates |
| `openemis_lesson` | `openemis_core` | Lesson planning, scheme of work |
| `openemis_lms` | `openemis_core` | Learning Management System, online courses, materials |
| `openemis_mentorship` | `openemis_core` | Mentor registration, mentorship sessions, group forums, DMs |
| `openemis_blog` | `openemis_core` | Educational blog for mentors, teachers, professionals |
| `openemis_parent` | `openemis_core` | Parent portal, parent–student linking, parent communications |
| `openemis_fees` | `openemis_core`, `account` | Fee structures, invoicing, payment tracking, financial reports |

---

### Level 3 — Dependent on Level 2 Modules

| Module | Depends On | Provides |
|--------|-----------|---------|
| `openemis_exam` | `openemis_core`, `openemis_attendance` | Exam scheduling, mark sheets, result entry, grade reports |
| `openemis_cbc` | `openemis_core`, `openemis_exam` | Competency-Based Curriculum strands, competencies, CBC assessments |

---

### Level 4 — Dependent on Level 3 Modules

| Module | Depends On | Provides |
|--------|-----------|---------|
| `openemis_grading` | `openemis_exam` | Grading system configuration, grade boundaries, GPA calculation |
| `openemis_digiguide` | `openemis_cbc`, `openemis_exam` | Digital Career Guidance, CBC performance tracking, KCSE prediction, KUCCPS integration |

---

### Special Modules

| Module | Depends On | Provides |
|--------|-----------|---------|
| `openemis_erp` | ALL openEMIS modules | Meta-module — no code, just declares dependencies on all other modules. Install this for a complete one-click setup. |
| `theme_web_openemis` | `web` | Custom UI theme — colors, fonts, logo, layout overrides for the Odoo web client |

---

## Installation Order

If installing modules individually (not using `openemis_erp`), follow this order:

```
1. openemis_core
2. openemis_fees          (needs account)
3. openemis_exam
4. openemis_cbc
5. openemis_grading
6. openemis_digiguide
7. All Level 2 modules (any order)
8. theme_web_openemis     (last — purely cosmetic)
```

Or simply install `openemis_erp` which handles all dependencies automatically.

---

## Minimum Install (Lightweight)

For a school that only needs the basics:

```
openemis_core
openemis_admission
openemis_attendance
openemis_exam
openemis_grading
openemis_fees
openemis_timetable
```

---

## CBC-Focused Install (Kenya)

For Kenyan schools implementing CBC:

```
openemis_core
openemis_admission
openemis_attendance
openemis_exam
openemis_grading
openemis_cbc
openemis_digiguide
openemis_fees
openemis_timetable
openemis_lesson
openemis_lms
openemis_library
openemis_parent
```

---

## Module File Counts

| Module | Models | Views | Controllers |
|--------|--------|-------|-------------|
| `openemis_core` | ~8 | ~15 | 1 |
| `openemis_exam` | ~5 | ~10 | 0 |
| `openemis_fees` | ~6 | ~12 | 1 |
| `openemis_digiguide` | ~4 | ~8 | 1 |
| `openemis_mentorship` | ~5 | ~10 | 1 |
| `openemis_lms` | ~4 | ~8 | 1 |
| `openemis_cbc` | ~4 | ~8 | 0 |
| Other modules | ~2–4 | ~4–8 | 0–1 |

---

## Adding a New Module to the Dependency Map

When you create a new module:

1. Declare its dependencies accurately in `__manifest__.py` under `'depends'`
2. Add it to `openemis_erp/__manifest__.py` `'depends'` list
3. Update this document with the new module's row in the appropriate level table
4. If it introduces new Odoo base dependencies (e.g., `account`, `hr`), note that in Level 0
