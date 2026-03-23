# v2 Developer Guide

## Setup

### Backend

```bash
cd versions/v2

python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/macOS

pip install -r requirements.txt

# Create .env (copy from v1 .env.example and adjust)
# Minimum: DATABASE_URL, SECRET_KEY

uvicorn app.main:app --reload --port 8001
```

API: http://localhost:8001  
Docs: http://localhost:8001/api/docs

### Frontend

```bash
cd versions/v2/web

npm install

# Create web/.env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > .env.local

npm run dev
```

Frontend: http://localhost:3000

---

## Adding a New Backend Endpoint

Same pattern as v1, but use `api/v2/` paths and register in `app/api/v2/router.py`.

```python
# app/api/v2/endpoints/my_module.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user

router = APIRouter()

@router.get("/")
def list_items(db: Session = Depends(get_db)):
    ...
```

Register in `app/api/v2/router.py`:
```python
from app.api.v2.endpoints import my_module
api_router.include_router(my_module.router, prefix="/my-module", tags=["My Module"])
```

---

## Adding a New Frontend Page

### 1. Create the page route

```
web/src/app/(dashboard)/my-module/page.tsx
```

```typescript
import { PageShell } from '@/components/shared/PageShell'
import { MyModuleTable } from './components/MyModuleTable'

export default function MyModulePage() {
  return (
    <PageShell title="My Module">
      <MyModuleTable />
    </PageShell>
  )
}
```

### 2. Add to sidebar navigation

`web/src/components/layout/Sidebar.tsx` — add a nav item:
```typescript
{ href: '/my-module', label: 'My Module', icon: SomeIcon, roles: ['admin'] }
```

### 3. Create the data table component

```typescript
// web/src/app/(dashboard)/my-module/components/MyModuleTable.tsx
'use client'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'

export function MyModuleTable() {
  const { data, isLoading } = useQuery({
    queryKey: ['my-module'],
    queryFn: () => api.get('/my-module/').then(r => r.data)
  })

  if (isLoading) return <div>Loading...</div>

  return (
    <DataTable columns={columns} data={data?.items ?? []} />
  )
}
```

### 4. Define TypeScript types

`web/src/types/index.ts`:
```typescript
export interface MyEntity {
  id: number
  name: string
  created_at: string
}
```

---

## Role-Based Access Control (Frontend)

### Protecting a page by role

Wrap the page content with `RoleGuard`:
```typescript
import { RoleGuard } from '@/components/layout/RoleGuard'

export default function AdminOnlyPage() {
  return (
    <RoleGuard allowedRoles={['admin']}>
      <PageContent />
    </RoleGuard>
  )
}
```

### Hiding UI elements by role

```typescript
import { useAuthStore } from '@/lib/auth'

function ActionButtons() {
  const { user } = useAuthStore()

  return (
    <div>
      {user?.role === 'admin' && (
        <Button>Delete</Button>
      )}
    </div>
  )
}
```

---

## Form Handling

Use React Hook Form + Zod for all forms:

```typescript
'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'

const schema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email'),
})

type FormData = z.infer<typeof schema>

export function CreateStudentForm({ onSuccess }: { onSuccess: () => void }) {
  const queryClient = useQueryClient()
  const form = useForm<FormData>({ resolver: zodResolver(schema) })

  const mutation = useMutation({
    mutationFn: (data: FormData) => api.post('/core/students/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['students'] })
      onSuccess()
    }
  })

  return (
    <form onSubmit={form.handleSubmit((data) => mutation.mutate(data))}>
      <input {...form.register('name')} />
      {form.formState.errors.name && <p>{form.formState.errors.name.message}</p>}
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Saving...' : 'Save'}
      </button>
    </form>
  )
}
```

---

## Adding a shadcn/ui Component

```bash
cd versions/v2/web
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add form
```

Components are added to `web/src/components/ui/`.

---

## Running the Frontend Build

```bash
cd versions/v2/web

# Type check
npx tsc --noEmit

# Lint
npm run lint

# Production build
npm run build

# Start production server
npm start
```

---

## API Client Usage

```typescript
import api from '@/lib/api'

// GET
const students = await api.get('/core/students/', { params: { page: 1 } })

// POST
const newStudent = await api.post('/core/students/', { name: 'John', ... })

// PUT
const updated = await api.put(`/core/students/${id}`, { name: 'Jane' })

// DELETE
await api.delete(`/core/students/${id}`)
```

The Axios instance automatically attaches the JWT token and handles 401 redirects.

---

## Environment Variables

| Variable | Where | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `versions/v2/.env` | PostgreSQL connection |
| `SECRET_KEY` | `versions/v2/.env` | JWT signing key |
| `CORS_ORIGINS` | `versions/v2/.env` | Allowed frontend origins |
| `NEXT_PUBLIC_API_URL` | `versions/v2/web/.env.local` | Backend URL for frontend |
