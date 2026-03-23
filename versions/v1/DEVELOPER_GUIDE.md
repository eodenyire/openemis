# v1 Developer Guide

## Setting Up Your Development Environment

```bash
cd versions/v1

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Install dev tools
pip install black flake8 pylint pytest pytest-cov

# Configure environment
cp .env.example .env
# Edit .env — minimum required: DATABASE_URL, SECRET_KEY

# Initialize database
python quickstart.py

# Start dev server (auto-reload)
python run.py
```

API: http://localhost:8000  
Docs: http://localhost:8000/api/docs  
ReDoc: http://localhost:8000/api/redoc

---

## Adding a New Endpoint

### 1. Create the model (if new table needed)

`app/models/my_module.py`:
```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class MyEntity(Base):
    __tablename__ = "my_entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"))

    student = relationship("Student", back_populates="my_entities")
```

### 2. Create the Pydantic schema

`app/schemas/my_module.py`:
```python
from pydantic import BaseModel
from typing import Optional

class MyEntityBase(BaseModel):
    name: str

class MyEntityCreate(MyEntityBase):
    student_id: int

class MyEntityResponse(MyEntityBase):
    id: int
    student_id: int

    class Config:
        from_attributes = True
```

### 3. Create the endpoint

`app/api/v1/endpoints/my_module.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.my_module import MyEntity
from app.schemas.my_module import MyEntityCreate, MyEntityResponse
from app.models.users import User

router = APIRouter()

@router.get("/", response_model=list[MyEntityResponse])
def list_entities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(MyEntity).all()

@router.post("/", response_model=MyEntityResponse)
def create_entity(
    payload: MyEntityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entity = MyEntity(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity
```

### 4. Register the router

`app/api/v1/router.py`:
```python
from app.api.v1.endpoints import my_module

api_router.include_router(
    my_module.router,
    prefix="/my-module",
    tags=["My Module"]
)
```

### 5. Create and apply migration

```bash
alembic revision --autogenerate -m "add my_entities table"
alembic upgrade head
```

---

## Adding a New Service

For business logic that spans multiple models or calls external APIs:

`app/services/my_service.py`:
```python
from sqlalchemy.orm import Session
from app.models.my_module import MyEntity

def calculate_something(entity_id: int, db: Session) -> dict:
    """Business logic here — keep endpoints thin."""
    entity = db.query(MyEntity).filter(MyEntity.id == entity_id).first()
    if not entity:
        raise ValueError(f"Entity {entity_id} not found")
    # ... logic ...
    return {"result": "value"}
```

Then call from the endpoint:
```python
from app.services.my_service import calculate_something

@router.get("/{id}/calculate")
def calculate(id: int, db: Session = Depends(get_db)):
    return calculate_something(id, db)
```

---

## Role-Based Access Control

Restrict endpoints to specific roles using dependency injection:

```python
from app.api.deps import get_current_user, require_role
from app.models.users import User, UserRole

@router.delete("/{id}")
def delete_entity(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    # Only admins reach here
    ...
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run a specific test file
pytest tests/test_api.py -v

# Run a specific test
pytest tests/test_api.py::test_login -v
```

---

## Linting and Formatting

```bash
# Format code
black app/

# Lint
flake8 app/ --config cfg_run_flake8.cfg
pylint app/ --rcfile cfg_run_pylint.cfg
```

Pre-commit hooks are configured in `.pre-commit-config.yaml`:
```bash
pip install pre-commit
pre-commit install
```

---

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description of change"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# View migration history
alembic history

# View current revision
alembic current
```

---

## Seeding Demo Data

```bash
# Phase 1: Academic structure (years, terms, courses, subjects)
python scripts/seed_phase1.py

# Phase 2: Students and faculty
python scripts/seed_phase2.py

# Phase 3: Enrollment and timetable
python scripts/seed_phase3.py

# Phase 4: Attendance records
python scripts/seed_phase4.py

# Phase 5: Exam results and fees
python scripts/seed_phase5.py

# Phase 6: Library, hostel, transport
python scripts/seed_phase6.py

# Kenya-specific data
python scripts/seed_kenya.py
```

---

## Debugging

### Enable debug logging

In `.env`:
```env
DEBUG=True
```

### Check database queries

Add to `app/db/session.py` temporarily:
```python
engine = create_engine(settings.DATABASE_URL, echo=True)  # echo=True logs all SQL
```

### Diagnose system issues

```bash
python scripts/diagnose.py
```

---

## Common Patterns

### Pagination

```python
from fastapi import Query

@router.get("/")
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    total = db.query(MyEntity).count()
    items = db.query(MyEntity).offset(skip).limit(limit).all()
    return {"items": items, "total": total, "skip": skip, "limit": limit}
```

### Filtering

```python
@router.get("/")
def list_students(
    class_id: Optional[int] = None,
    academic_year: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Student)
    if class_id:
        query = query.filter(Student.class_id == class_id)
    if academic_year:
        query = query.filter(Student.academic_year == academic_year)
    return query.all()
```

### Error Handling

```python
from fastapi import HTTPException

# 404
raise HTTPException(status_code=404, detail="Student not found")

# 400
raise HTTPException(status_code=400, detail="Student already enrolled")

# 403
raise HTTPException(status_code=403, detail="Insufficient permissions")
```
