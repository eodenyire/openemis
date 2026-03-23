# openemis_admission — Admissions Module

Manages the full student admissions and enrolment workflow from application to registration.

## Models
- `op.admission` — Admission applications with applicant details, program applied for, status
- `op.admission.register` — Admission registers per academic year and course

## Key Features
- Configurable admission stages (applied, under review, admitted, rejected)
- Admission register per course/batch
- Automatic student record creation on admission confirmation
- Printable admission letters
- Demo data included

## Depends On
`openemis_core`
