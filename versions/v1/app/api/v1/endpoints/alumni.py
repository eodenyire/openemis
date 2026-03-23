"""Alumni endpoints — uses student_lifecycle.Alumni (alumni_records table)."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.student_lifecycle import Alumni

router = APIRouter()


class AlumniCreate(BaseModel):
    student_id: int
    graduation_year: int
    final_grade: Optional[str] = None
    current_institution: Optional[str] = None
    current_employer: Optional[str] = None
    career_path: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None

class AlumniUpdate(BaseModel):
    current_institution: Optional[str] = None
    current_employer: Optional[str] = None
    career_path: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None


@router.get("/")
def list_alumni(
    graduation_year: Optional[int] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(Alumni)
    if graduation_year: q = q.filter_by(graduation_year=graduation_year)
    total = q.count()
    items = q.order_by(Alumni.graduation_year.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": a.id, "student_id": a.student_id,
         "graduation_year": a.graduation_year, "final_grade": a.final_grade,
         "current_institution": a.current_institution,
         "current_employer": a.current_employer,
         "career_path": a.career_path,
         "contact_email": a.contact_email}
        for a in items
    ]}

@router.post("/", status_code=201)
def create_alumni(data: AlumniCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    existing = db.query(Alumni).filter_by(student_id=data.student_id).first()
    if existing: raise HTTPException(400, "Alumni record already exists for this student")
    obj = Alumni(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "student_id": obj.student_id, "graduation_year": obj.graduation_year}

@router.get("/{id}")
def get_alumni(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Alumni).filter_by(id=id).first()
    if not obj: raise HTTPException(404, "Alumni record not found")
    return {"id": obj.id, "student_id": obj.student_id,
            "graduation_year": obj.graduation_year, "final_grade": obj.final_grade,
            "current_institution": obj.current_institution,
            "current_employer": obj.current_employer,
            "career_path": obj.career_path,
            "contact_email": obj.contact_email, "contact_phone": obj.contact_phone,
            "notes": obj.notes}

@router.put("/{id}")
def update_alumni(id: int, data: AlumniUpdate, db: Session = Depends(get_db),
                  _=Depends(get_current_user)):
    obj = db.query(Alumni).filter_by(id=id).first()
    if not obj: raise HTTPException(404, "Alumni record not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "student_id": obj.student_id}

@router.delete("/{id}", status_code=204)
def delete_alumni(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Alumni).filter_by(id=id).first()
    if not obj: raise HTTPException(404, "Alumni record not found")
    db.delete(obj); db.commit()
