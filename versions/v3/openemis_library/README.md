# openemis_library — Library Module

Manages the school library — book catalog, member management, and issue/return tracking. Includes CBC-specific categorisation by grade level, subject, topic, and format.

## Models
- `op.library` — Book catalog (title, author, ISBN, category, format)
- `op.library.member` — Library members (students and staff)
- `op.book.issue` — Book issue and return records

## Key Features
- Book catalog with CBC grade-level (Grade 1–12), subject, topic, and format tagging (video, audio, PDF, Word, CSV, etc.)
- Member registration and card management
- Book issue, return, and renewal workflow
- Overdue tracking and fine calculation
- Library reports (issued books, overdue, inventory)

## Depends On
`openemis_core`
