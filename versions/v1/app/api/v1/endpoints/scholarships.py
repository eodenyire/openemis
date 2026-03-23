"""Scholarships & Bursaries endpoints."""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.extras import Scholarship, ScholarshipType

router = APIRouter()


class TypeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    amount: Optional[float] = None

class ScholarshipCreate(BaseModel):
    student_id: int
    scholarship_type_id: int
    amount: float
    start_date: date
    end_date: Optional[date] = None
    academic_year_id: Optional[int] = None
    note: Optional[str] = None

class ScholarshipUpdate(BaseModel):
    amount: Optional[float] = None
    end_date: Optional[date] = None
    state: Optional[str] = None
    note: Optional[str] = None


# ── Types ─────────────────────────────────────────────────────────────────────

@router.get("/types")
def list_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(ScholarshipType).filter_by(active=True).all()

@router.post("/types", status_code=201)
def create_type(data: TypeCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = ScholarshipType(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# ── Scholarships ──────────────────────────────────────────────────────────────

@router.get("/")
def list_scholarships(
    student_id: Optional[int] = None,
    state: Optional[str] = None,
    academic_year_id: Optional[int] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(Scholarship).filter_by(active=True)
    if student_id: q = q.filter_by(student_id=student_id)
    if state: q = q.filter_by(state=state)
    if academic_year_id: q = q.filter_by(academic_year_id=academic_year_id)
    total = q.count()
    items = q.order_by(Scholarship.start_date.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": s.id, "student_id": s.student_id,
         "type": s.scholarship_type.name if s.scholarship_type else None,
         "amount": s.amount, "start_date": s.start_date,
         "end_date": s.end_date, "state": s.state}
        for s in items
    ]}

@router.post("/", status_code=201)
def create_scholarship(data: ScholarshipCreate, db: Session = Depends(get_db),
                       _=Depends(get_current_user)):
    obj = Scholarship(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "student_id": obj.student_id, "amount": obj.amount, "state": obj.state}

@router.get("/{id}")
def get_scholarship(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Scholarship).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Scholarship not found")
    return {"id": obj.id, "student_id": obj.student_id,
            "type": obj.scholarship_type.name if obj.scholarship_type else None,
            "amount": obj.amount, "start_date": obj.start_date,
            "end_date": obj.end_date, "state": obj.state, "note": obj.note}

@router.put("/{id}")
def update_scholarship(id: int, data: ScholarshipUpdate, db: Session = Depends(get_db),
                       _=Depends(get_current_user)):
    obj = db.query(Scholarship).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Scholarship not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "state": obj.state, "amount": obj.amount}

@router.delete("/{id}", status_code=204)
def delete_scholarship(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Scholarship).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Scholarship not found")
    obj.active = False; db.commit()
