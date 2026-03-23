# web — Next.js Frontend (v2)

The Next.js 14 frontend for openEMIS v2. A modern, TypeScript-first web application with a professional component library, role-based access control, and a clean dashboard layout.

## Tech Stack

- Next.js 14.2.5 (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui
- Radix UI primitives
- TanStack React Query (data fetching)
- Zustand (state management)
- React Hook Form + Zod (form validation)
- Axios (HTTP client)
- Lucide React (icons)

## Structure

```
web/src/
├── app/                        # Next.js App Router
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Root redirect
│   ├── providers.tsx           # React Query + auth providers
│   ├── globals.css             # Global styles
│   ├── (dashboard)/            # Protected dashboard routes
│   │   ├── layout.tsx          # Dashboard shell (sidebar + header)
│   │   └── dashboard/          # Main dashboard page
│   ├── login/                  # Login page
│   └── unauthorized/           # 403 page
├── components/
│   ├── layout/                 # Layout components
│   │   ├── AuthGuard.tsx       # Redirects unauthenticated users
│   │   ├── RoleGuard.tsx       # Restricts access by user role
│   │   ├── Sidebar.tsx         # Navigation sidebar
│   │   └── Header.tsx          # Top header bar
│   ├── shared/                 # Reusable page components
│   │   ├── DataTable.tsx       # Generic sortable/filterable table
│   │   ├── StatCard.tsx        # Dashboard metric card
│   │   ├── PageShell.tsx       # Standard page wrapper with title/actions
│   │   └── ReportDownloadButton.tsx  # PDF/Excel download trigger
│   └── ui/                     # shadcn/ui primitives
│       ├── button.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       ├── dropdown-menu.tsx
│       ├── input.tsx
│       ├── label.tsx
│       ├── select.tsx
│       ├── skeleton.tsx
│       ├── table.tsx
│       ├── tabs.tsx
│       ├── avatar.tsx
│       └── badge.tsx
├── lib/
│   ├── api.ts                  # Axios instance with auth interceptors
│   ├── auth.ts                 # Auth helpers (token storage, user info)
│   └── utils.ts                # Tailwind class merging (cn utility)
└── types/
    └── index.ts                # Shared TypeScript interfaces
```

## Key Concepts

### Auth Flow
`AuthGuard` wraps all dashboard routes. On load it checks for a valid JWT in storage — unauthenticated users are redirected to `/login`. After login the token is stored and the user is redirected to `/dashboard`.

### Role-Based Access
`RoleGuard` accepts a `roles` prop and renders children only if the current user's role matches. Otherwise redirects to `/unauthorized`.

### Data Fetching
All API calls go through the Axios instance in `lib/api.ts` which automatically attaches the `Authorization: Bearer <token>` header. React Query handles caching, loading states, and refetching.

### Forms
React Hook Form manages form state. Zod schemas define validation rules. `@hookform/resolvers/zod` connects them.

## Setup

```bash
npm install
npm run dev       # http://localhost:3000
npm run build     # production build
npm run lint      # ESLint
```

Set `NEXT_PUBLIC_API_URL` in `.env.local` to point to the v2 FastAPI backend.
