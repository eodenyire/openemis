# openemis_digiguide — Digital Career Guidance Module

Tracks CBC academic performance and provides career guidance by predicting national exam results and matching students to eligible careers via KUCCPS integration.

## Models
- `op.digiguide.profile` — Student career guidance profile
- `op.digiguide.assessment` — CBC assessment records (weekly, mid-term, termly, annual)
- `op.digiguide.prediction` — National exam result predictions (Grade 3, 6, 9, 12)
- `op.digiguide.career` — Career options from KUCCPS
- `op.digiguide.career.match` — Student-career eligibility matches

## Key Features
- CBC performance tracking across all assessment types
- Weighted average calculation for national exam prediction
- KUCCPS API integration to fetch university/college career requirements
- Career eligibility matching per student
- Student-facing career guidance dashboard
- Roadmap: ML-based prediction engine upgrade

## Depends On
`openemis_core`, `openemis_cbc`
