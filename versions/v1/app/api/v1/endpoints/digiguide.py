"""DigiGuide — Career Guidance & Academic Performance endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.extras import (
    CareerPath, StudentCareerMatch, AcademicPerformance,
)

router = APIRouter()


# ── Career Paths ──────────────────────────────────────────────────────────────

class CareerPathCreate(BaseModel):
    name: str
    description: Optional[str] = None
    min_grade: Optional[str] = None
    required_subjects: Optional[str] = None   # JSON string
    university_requirements: Optional[str] = None

class CareerMatchCreate(BaseModel):
    student_id: int
    career_id: int
    match_score: Optional[float] = None
    predicted_grade: Optional[str] = None
    recommendation: Optional[str] = None


@router.get("/careers")
def list_careers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    careers = db.query(CareerPath).filter_by(active=True).all()
    return [{"id": c.id, "name": c.name, "description": c.description,
             "min_grade": c.min_grade, "required_subjects": c.required_subjects}
            for c in careers]

@router.post("/careers", status_code=201)
def create_career(data: CareerPathCreate, db: Session = Depends(get_db),
                  _=Depends(get_current_user)):
    obj = CareerPath(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "name": obj.name}

@router.get("/careers/{id}")
def get_career(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(CareerPath).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Career path not found")
    return {"id": obj.id, "name": obj.name, "description": obj.description,
            "min_grade": obj.min_grade, "required_subjects": obj.required_subjects,
            "university_requirements": obj.university_requirements}

@router.put("/careers/{id}")
def update_career(id: int, data: CareerPathCreate, db: Session = Depends(get_db),
                  _=Depends(get_current_user)):
    obj = db.query(CareerPath).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Career path not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "name": obj.name}

@router.delete("/careers/{id}", status_code=204)
def delete_career(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(CareerPath).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Career path not found")
    obj.active = False; db.commit()


# ── Student Career Matches ────────────────────────────────────────────────────

@router.get("/matches")
def list_matches(
    student_id: Optional[int] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(StudentCareerMatch)
    if student_id: q = q.filter_by(student_id=student_id)
    total = q.count()
    items = q.order_by(StudentCareerMatch.match_score.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": m.id, "student_id": m.student_id,
         "career": m.career.name if m.career else None,
         "match_score": m.match_score, "predicted_grade": m.predicted_grade,
         "recommendation": m.recommendation, "created_at": m.created_at}
        for m in items
    ]}

@router.post("/matches", status_code=201)
def create_match(data: CareerMatchCreate, db: Session = Depends(get_db),
                 _=Depends(get_current_user)):
    obj = StudentCareerMatch(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "student_id": obj.student_id, "match_score": obj.match_score}

@router.get("/students/{student_id}/matches")
def student_matches(student_id: int, db: Session = Depends(get_db),
                    _=Depends(get_current_user)):
    matches = (db.query(StudentCareerMatch)
               .filter_by(student_id=student_id)
               .order_by(StudentCareerMatch.match_score.desc()).all())
    return [{"career": m.career.name if m.career else None,
             "match_score": m.match_score, "predicted_grade": m.predicted_grade,
             "recommendation": m.recommendation}
            for m in matches]


# ── Academic Performance ──────────────────────────────────────────────────────

class PerformanceCreate(BaseModel):
    student_id: int
    subject_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    academic_term_id: Optional[int] = None
    assignment_score: Optional[float] = None
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None
    total_score: Optional[float] = None
    grade: Optional[str] = None


@router.get("/performance")
def list_performance(
    student_id: Optional[int] = None,
    academic_year_id: Optional[int] = None,
    academic_term_id: Optional[int] = None,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(AcademicPerformance)
    if student_id: q = q.filter_by(student_id=student_id)
    if academic_year_id: q = q.filter_by(academic_year_id=academic_year_id)
    if academic_term_id: q = q.filter_by(academic_term_id=academic_term_id)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": p.id, "student_id": p.student_id,
         "subject": p.subject.name if p.subject else None,
         "assignment_score": p.assignment_score, "midterm_score": p.midterm_score,
         "final_score": p.final_score, "total_score": p.total_score, "grade": p.grade}
        for p in items
    ]}

@router.post("/performance", status_code=201)
def create_performance(data: PerformanceCreate, db: Session = Depends(get_db),
                       _=Depends(get_current_user)):
    obj = AcademicPerformance(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "student_id": obj.student_id, "grade": obj.grade}
