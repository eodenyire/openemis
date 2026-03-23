# openemis_cbc — Competency-Based Curriculum Module

Implements Kenya's Competency-Based Curriculum (CBC) framework within openEMIS, supporting strand-based assessment and learning outcomes tracking.

## Models
- `op.cbc.strand` — CBC learning strands
- `op.cbc.sub.strand` — Sub-strands
- `op.cbc.learning.outcome` — Learning outcomes per strand
- `op.cbc.assessment` — Student assessments per learning outcome
- `op.cbc.report` — CBC progress reports

## Key Features
- Full CBC strand and sub-strand hierarchy
- Learning outcome definitions per grade level
- Formative and summative assessment recording
- CBC-style progress reports (Exceeds Expectation, Meets Expectation, Approaches Expectation, Below Expectation)
- Integration with openemis_digiguide for career prediction

## Depends On
`openemis_core`
