"""Alumni endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.extras import OpAlumni

router = APIRouter()


@router.get("/alumni")
def list_alumni(graduation_year: Optional[int] = None, skip: int = 0, limit: int = 100,
                db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpAlumni).filter_by(active=True)
    if graduation_year: q = q.filter_by(graduation_year=graduation_year)
    return {"total": q.count(), "items": q.offset(skip).limit(limit).all()}

@router.post("/alumni", status_code=201)
def create_alumni(student_id: int, graduation_year: Optional[int] = None,
                  current_institution: Optional[str] = None, current_employer: Optional[str] = None,
                  email: Optional[str] = None, phone: Optional[str] = None,
                  db: Session = Depends(get_db), _=Depends(require_admin)):
    existing = db.query(OpAlumni).filter_by(student_id=student_id).first()
    if existing: raise HTTPException(409, "Alumni record already exists for this student")
    obj = OpAlumni(student_id=student_id, graduation_year=graduation_year,
                   current_institution=current_institution, current_employer=current_employer,
                   email=email, phone=phone)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/alumni/{id}")
def get_alumni(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpAlumni).get(id)
    if not obj: raise HTTPException(404, "Alumni not found")
    return obj

@router.put("/alumni/{id}")
def update_alumni(id: int, current_institution: Optional[str] = None,
                  current_employer: Optional[str] = None, email: Optional[str] = None,
                  phone: Optional[str] = None,
                  db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpAlumni).get(id)
    if not obj: raise HTTPException(404, "Alumni not found")
    if current_institution is not None: obj.current_institution = current_institution
    if current_employer is not None: obj.current_employer = current_employer
    if email is not None: obj.email = email
    if phone is not None: obj.phone = phone
    db.commit(); db.refresh(obj); return obj
