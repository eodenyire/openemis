# openemis_core — Foundation Module

The base module for the entire openEMIS system. All other modules depend on this one. It provides the core data models for students, faculty, courses, programs, academic years, and institutional configuration.

## Models
- `op.student` — Student profiles, registration numbers, personal details
- `op.faculty` — Faculty/teacher profiles
- `op.course` — Course definitions
- `op.batch` — Course batches/classes
- `op.subject` — Subject definitions
- `op.program` — Academic programs
- `op.program.level` — Program levels (certificate, diploma, degree)
- `op.department` — Departments
- `op.academic.year` — Academic years
- `op.academic.term` — Academic terms/semesters
- `op.subject.registration` — Student subject registrations

## Key Features
- Student and faculty portals (Odoo Website)
- Student ID card and bonafide certificate reports
- Dashboard with key metrics
- CBC (Competency-Based Curriculum) configuration
- Multi-company support

## Depends On
`board`, `hr`, `web`, `website`
