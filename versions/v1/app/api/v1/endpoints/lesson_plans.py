"""Lesson Planning endpoints — Schemes of Work, Lesson Plans, Teaching Resources."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, require_teacher
from app.models.lms import (
    SchemeOfWork, LessonPlan, LessonPlanStatus, TeachingResource, ResourceType,
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class SchemeCreate(BaseModel):
    title: str
    course_id: int
    subject_id: int
    teacher_id: int
    academic_year_id: int
    academic_term_id: int

class SchemeOut(BaseModel):
    id: int; title: str; course_id: int; subject_id: int
    teacher_id: int; status: str
    class Config: from_attributes = True

class LessonCreate(BaseModel):
    title: str
    week_number: int
    lesson_number: int = 1
    sub_strand_id: Optional[int] = None
    objectives: Optional[str] = None
    activities: Optional[str] = None
    resources_needed: Optional[str] = None
    assessment_method: Optional[str] = None
    duration_minutes: int = 40

class LessonOut(BaseModel):
    id: int; scheme_id: int; title: str; week_number: int
    lesson_number: int; status: str; duration_minutes: int
    class Config: from_attributes = True

class ResourceCreate(BaseModel):
    title: str
    description: Optional[str] = None
    resource_type: str = "document"
    url: Optional[str] = None
    subject_id: Optional[int] = None
    course_id: Optional[int] = None
    uploaded_by_id: int
    is_public: bool = False

class ResourceOut(BaseModel):
    id: int; title: str; resource_type: str
    url: Optional[str]; is_public: bool
    class Config: from_attributes = True


# ── Schemes of Work ───────────────────────────────────────────────────────────

@router.get("/schemes", response_model=List[SchemeOut])
def list_schemes(skip: int = 0, limit: int = 50, db: Session = Depends(get_db),
                 _=Depends(get_current_user)):
    return db.query(SchemeOfWork).offset(skip).limit(limit).all()

@router.post("/schemes", response_model=SchemeOut, status_code=201)
def create_scheme(data: SchemeCreate, db: Session = Depends(get_db),
                  _=Depends(require_teacher)):
    obj = SchemeOfWork(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/schemes/{id}", response_model=SchemeOut)
def get_scheme(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(SchemeOfWork).get(id)
    if not obj: raise HTTPException(404, "Scheme not found")
    return obj

@router.get("/schemes/{id}/lessons", response_model=List[LessonOut])
def list_lessons(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(LessonPlan).filter_by(scheme_id=id).order_by(
        LessonPlan.week_number, LessonPlan.lesson_number).all()

@router.post("/schemes/{id}/lessons", response_model=LessonOut, status_code=201)
def create_lesson(id: int, data: LessonCreate, db: Session = Depends(get_db),
                  _=Depends(require_teacher)):
    if not db.query(SchemeOfWork).get(id):
        raise HTTPException(404, "Scheme not found")
    obj = LessonPlan(scheme_id=id, **data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/lessons/{id}/approve")
def approve_lesson(id: int, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    lesson = db.query(LessonPlan).get(id)
    if not lesson: raise HTTPException(404, "Lesson plan not found")
    lesson.status = LessonPlanStatus.APPROVED
    db.commit()
    return {"id": lesson.id, "status": lesson.status}

@router.put("/lessons/{id}/submit")
def submit_lesson(id: int, db: Session = Depends(get_db), _=Depends(require_teacher)):
    lesson = db.query(LessonPlan).get(id)
    if not lesson: raise HTTPException(404, "Lesson plan not found")
    lesson.status = LessonPlanStatus.SUBMITTED
    db.commit()
    return {"id": lesson.id, "status": lesson.status}

@router.put("/schemes/{id}/approve")
def approve_scheme(id: int, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    scheme = db.query(SchemeOfWork).get(id)
    if not scheme: raise HTTPException(404, "Scheme not found")
    scheme.status = LessonPlanStatus.APPROVED
    scheme.approved_at = datetime.utcnow()
    db.commit()
    return {"id": scheme.id, "status": scheme.status}


# ── Teaching Resources ────────────────────────────────────────────────────────

@router.get("/resources", response_model=List[ResourceOut])
def list_resources(skip: int = 0, limit: int = 50, subject_id: Optional[int] = None,
                   db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(TeachingResource)
    if subject_id: q = q.filter_by(subject_id=subject_id)
    return q.offset(skip).limit(limit).all()

@router.post("/resources", response_model=ResourceOut, status_code=201)
def create_resource(data: ResourceCreate, db: Session = Depends(get_db),
                    _=Depends(require_teacher)):
    obj = TeachingResource(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/resources/{id}", response_model=ResourceOut)
def get_resource(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(TeachingResource).get(id)
    if not obj: raise HTTPException(404, "Resource not found")
    return obj

@router.delete("/resources/{id}", status_code=204)
def delete_resource(id: int, db: Session = Depends(get_db), _=Depends(require_teacher)):
    obj = db.query(TeachingResource).get(id)
    if not obj: raise HTTPException(404, "Resource not found")
    db.delete(obj); db.commit()
