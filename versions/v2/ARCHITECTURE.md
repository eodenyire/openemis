# v2 Architecture — FastAPI + Next.js Full-Stack

## Overview

v2 is a decoupled full-stack application. The FastAPI backend and Next.js frontend are completely independent processes that communicate over HTTP. The backend exposes a REST API; the frontend consumes it via React Query and Axios.

---

## System Diagram

```
Browser
    │
    ▼
Next.js 14 (App Router) — localhost:3000
    │
    ├── Server Components (SSR where possible)
    ├── Client Components (interactive UI)
    ├── AuthGuard (redirects to /login if no token)
    ├── RoleGuard (redirects to /unauthorized if wrong role)
    │
    ▼  (HTTP/JSON — Authorization: Bearer <token>)
FastAPI Backend — localhost:8001
    │
    ├── CORS middleware
    ├── JWT validation (deps.py)
    ├── Endpoint handlers (api/v2/endpoints/)
    ├── SQLAlchemy ORM (models/)
    │
    ▼
PostgreSQL Database
```

---

## Backend Structure

```
app/
├── main.py              # App factory, CORS, router registration
├── api/
│   ├── deps.py          # get_db, get_current_user
│   └── v2/
│       ├── router.py    # Aggregates all endpoint routers
│       └── endpoints/   # One file per domain
├── core/
│   ├── config.py        # Pydantic Settings
│   └── security.py      # JWT, bcrypt
├── db/
│   ├── base.py          # SQLAlchemy Base
│   └── session.py       # Engine + SessionLocal
├── models/              # SQLAlchemy models (reverse-engineered from openeducat)
└── schemas/             # Pydantic schemas
```

### Key Difference from v1

v2 backend models were reverse-engineered from the openeducat Odoo modules. This gives v2 a richer domain model that more closely mirrors the Odoo data structure, making it easier to migrate data between v2 and v3.

---

## Frontend Structure

```
web/src/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout (providers)
│   ├── (dashboard)/              # Route group — all protected routes
│   │   ├── layout.tsx            # Dashboard layout (sidebar + header)
│   │   ├── page.tsx              # Dashboard home
│   │   ├── students/             # Students module
│   │   ├── faculty/              # Faculty module
│   │   ├── courses/              # Courses module
│   │   ├── admissions/           # Admissions module
│   │   ├── attendance/           # Attendance module
│   │   ├── exams/                # Exams module
│   │   ├── fees/                 # Fees module
│   │   ├── library/              # Library module
│   │   └── timetable/            # Timetable module
│   ├── login/                    # Public auth page
│   └── unauthorized/             # Access denied page
├── components/
│   ├── layout/
│   │   ├── AuthGuard.tsx         # Redirects unauthenticated users
│   │   ├── RoleGuard.tsx         # Restricts by role
│   │   ├── Sidebar.tsx           # Navigation sidebar
│   │   └── Header.tsx            # Top header bar
│   ├── shared/
│   │   ├── DataTable.tsx         # Reusable paginated table
│   │   ├── StatCard.tsx          # Dashboard stat card
│   │   └── PageShell.tsx         # Page wrapper with title/actions
│   └── ui/                       # shadcn/ui components
├── lib/
│   ├── api.ts                    # Axios instance + interceptors
│   ├── auth.ts                   # Auth helpers (token storage)
│   └── utils.ts                  # Shared utilities
└── types/                        # TypeScript type definitions
```

---

## State Management

### Auth State (Zustand)

```typescript
// Stored in localStorage, hydrated on app load
interface AuthStore {
  token: string | null
  user: UserProfile | null
  setToken: (token: string) => void
  setUser: (user: UserProfile) => void
  logout: () => void
}
```

### Server State (React Query)

All API data is managed by React Query:
- Automatic caching and background refetching
- Optimistic updates for mutations
- Pagination support via `useInfiniteQuery`
- Cache invalidation after mutations

```typescript
// Example: fetch students
const { data, isLoading } = useQuery({
  queryKey: ['students', { page, classId }],
  queryFn: () => api.get('/core/students/', { params: { page, class_id: classId } })
})

// Example: create student
const mutation = useMutation({
  mutationFn: (data) => api.post('/core/students/', data),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['students'] })
})
```

---

## Authentication Flow

```
1. User submits login form
   → POST /api/v2/auth/login
   → Receive { access_token }
   → Store in Zustand (persisted to localStorage)

2. Axios interceptor adds token to every request:
   Authorization: Bearer <token>

3. AuthGuard checks Zustand store on every route change:
   → No token → redirect to /login
   → Token present → allow through

4. RoleGuard checks user.role:
   → Wrong role → redirect to /unauthorized
   → Correct role → render page

5. Token expiry (60 min):
   → API returns 401
   → Axios interceptor catches 401
   → Clears Zustand store
   → Redirects to /login
```

---

## API Communication

`lib/api.ts` configures an Axios instance:

```typescript
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL + '/api/v2',
  headers: { 'Content-Type': 'application/json' }
})

// Request interceptor — attach token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response interceptor — handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

---

## Component Patterns

### Page Component

```typescript
// app/(dashboard)/students/page.tsx
export default function StudentsPage() {
  return (
    <PageShell title="Students" action={<CreateStudentButton />}>
      <StudentsTable />
    </PageShell>
  )
}
```

### Data Table

```typescript
// Uses the shared DataTable component
<DataTable
  columns={studentColumns}
  queryKey={['students']}
  fetchFn={(params) => api.get('/core/students/', { params })}
/>
```

### Form with Validation

```typescript
const schema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  class_id: z.number().int().positive()
})

const form = useForm<z.infer<typeof schema>>({
  resolver: zodResolver(schema)
})
```

---

## Environment Configuration

Backend `.env`:
```env
DATABASE_URL=postgresql://openemis:password@localhost:5432/openemis_v2
SECRET_KEY=long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=["http://localhost:3000"]
DEBUG=False
```

Frontend `web/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```
