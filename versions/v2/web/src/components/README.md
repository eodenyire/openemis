# src/components — React UI Components (v2)

Reusable React components that make up the openEMIS Next.js frontend.

## Organisation

Components are grouped by domain and type:

```
components/
├── ui/           # Base design system (buttons, inputs, cards, modals, badges)
├── layout/       # Shell, sidebar, topbar, breadcrumbs, page wrappers
├── auth/         # Login form, protected route wrapper
├── dashboard/    # Stats cards, charts, activity feed
├── students/     # Student list, detail card, enrollment form
├── faculty/      # Teacher list, subject assignment UI
├── admissions/   # Application form, status tracker
├── attendance/   # Attendance marking grid, summary charts
├── exams/        # Result entry table, grade report viewer
├── fees/         # Invoice list, M-Pesa payment modal
├── timetable/    # Weekly schedule grid
├── library/      # Book catalogue, issue/return forms
└── cbc/          # Strand assessment forms, portfolio viewer
```

## Tech Stack

- React 18 with TypeScript
- Tailwind CSS for styling
- shadcn/ui as the base component library
- Recharts for data visualisation
- React Hook Form + Zod for form validation

## Conventions

- All components are typed with TypeScript interfaces from `src/types/`
- Server components used where possible (Next.js App Router)
- Client components marked with `"use client"` only when interactivity is needed
