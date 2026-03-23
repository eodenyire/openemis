# openemis_exam — Examination Module

Manages exam scheduling, mark entry, grade configuration, and result processing.

## Models
- `op.exam` — Exam definitions (name, course, academic term)
- `op.exam.session` — Individual exam sessions per subject
- `op.exam.attendees` — Student exam attendance
- `op.marks.marks` — Mark entry per student per subject
- `op.grade.configuration` — Grade boundaries (A, B, C, etc.)
- `op.grade.line` — Grade line items

## Key Features
- Exam scheduling per course and term
- Mark sheet entry and bulk import
- Configurable grading scales
- Result slips and mark sheets (PDF reports)
- Grade calculation and GPA computation
- Exam result publishing

## Depends On
`openemis_core`
