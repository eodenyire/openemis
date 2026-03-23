"""Core academic endpoints: departments, programs, courses, batches, subjects, academic years/terms"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.api.crud import get_one, get_all, create_obj, update_obj, delete_obj
from app.models.core import (
    Department, Program, ProgramLevel, Course, Batch,
    Subject, AcademicYear, AcademicTerm, StudentCategory
)
from app.schemas.core import (
    DepartmentCreate, DepartmentUpdate, DepartmentOut,
    ProgramCreate, ProgramUpdate, ProgramOut,
    ProgramLevelCreate, ProgramLevelUpdate, ProgramLevelOut,
    CourseCreate, CourseUpdate, CourseOut,
    BatchCreate, BatchUpdate, BatchOut,
    SubjectCreate, SubjectUpdate, SubjectOut,
    AcademicYearCreate, AcademicYearUpdate, AcademicYearOut,
    AcademicTermCreate, AcademicTermUpdate, AcademicTermOut,
    StudentCategoryCreate, StudentCategoryUpdate, StudentCategoryOut,
)

router = APIRouter()

# ── Generic factory to avoid repeating the same 5 routes ─────────────────────
def _crud_routes(r, Model, CreateSchema, UpdateSchema, OutSchema, tag):
    @r.get("/", response_model=List[OutSchema], tags=[tag])
    def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
        return get_all(db, Model, skip, limit)

    @r.post("/", response_model=OutSchema, status_code=201, tags=[tag])
    def create_item(data: CreateSchema, db: Session = Depends(get_db),
                    _=Depends(require_admin)):
        return create_obj(db, Model, data.model_dump())

    @r.get("/{id}", response_model=OutSchema, tags=[tag])
    def get_item(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
        obj = get_one(db, Model, id)
        if not obj:
            raise HTTPException(404, f"{Model.__name__} not found")
        return obj

    @r.put("/{id}", response_model=OutSchema, tags=[tag])
    def update_item(id: int, data: UpdateSchema, db: Session = Depends(get_db),
                    _=Depends(require_admin)):
        obj = get_one(db, Model, id)
        if not obj:
            raise HTTPException(404, f"{Model.__name__} not found")
        return update_obj(db, obj, data.model_dump(exclude_unset=True))

    @r.delete("/{id}", status_code=204, tags=[tag])
    def delete_item(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
        obj = get_one(db, Model, id)
        if not obj:
            raise HTTPException(404, f"{Model.__name__} not found")
        delete_obj(db, obj)


# ── Sub-routers ───────────────────────────────────────────────────────────────
dept_router = APIRouter(prefix="/departments")
_crud_routes(dept_router, Department, DepartmentCreate, DepartmentUpdate, DepartmentOut, "Departments")

prog_level_router = APIRouter(prefix="/program-levels")
_crud_routes(prog_level_router, ProgramLevel, ProgramLevelCreate, ProgramLevelUpdate, ProgramLevelOut, "Program Levels")

prog_router = APIRouter(prefix="/programs")
_crud_routes(prog_router, Program, ProgramCreate, ProgramUpdate, ProgramOut, "Programs")

course_router = APIRouter(prefix="/courses")
_crud_routes(course_router, Course, CourseCreate, CourseUpdate, CourseOut, "Courses")

batch_router = APIRouter(prefix="/batches")
_crud_routes(batch_router, Batch, BatchCreate, BatchUpdate, BatchOut, "Batches")

subject_router = APIRouter(prefix="/subjects")
_crud_routes(subject_router, Subject, SubjectCreate, SubjectUpdate, SubjectOut, "Subjects")

year_router = APIRouter(prefix="/academic-years")
_crud_routes(year_router, AcademicYear, AcademicYearCreate, AcademicYearUpdate, AcademicYearOut, "Academic Years")

term_router = APIRouter(prefix="/academic-terms")
_crud_routes(term_router, AcademicTerm, AcademicTermCreate, AcademicTermUpdate, AcademicTermOut, "Academic Terms")

cat_router = APIRouter(prefix="/student-categories")
_crud_routes(cat_router, StudentCategory, StudentCategoryCreate, StudentCategoryUpdate, StudentCategoryOut, "Student Categories")

# Attach all to main router
for sub in [dept_router, prog_level_router, prog_router, course_router,
            batch_router, subject_router, year_router, term_router, cat_router]:
    router.include_router(sub)
