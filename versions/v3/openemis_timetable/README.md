# openemis_timetable — Timetable Module

Generates and manages class timetables for courses and batches.

## Models
- `op.timetable` — Timetable header per batch and academic term
- `op.timetable.line` — Individual timetable slots (day, time, subject, faculty, room)

## Key Features
- Visual timetable grid view
- Conflict detection (faculty and room double-booking)
- Printable timetable reports
- Per-student and per-faculty timetable views

## Depends On
`openemis_core`
