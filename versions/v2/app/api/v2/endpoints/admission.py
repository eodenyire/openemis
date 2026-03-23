"""Admission endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.admission import OpAdmissionRegister, OpAdmission

router = APIRouter()


@router.get("/admission-registers")
def list_registers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpAdmissionRegister).filter_by(active=True).all()

@router.post("/admission-registers", status_code=201)
def create_register(name: str, course_id: int, academic_year_id: int,
                    start_date: Optional[date] = None, end_date: Optional[date] = None,
                    max_seats: int = 0, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpAdmissionRegister(name=name, course_id=course_id, academic_year_id=academic_year_id,
                               start_date=start_date, end_date=end_date, max_seats=max_seats)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/admission-registers/{id}")
def get_register(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpAdmissionRegister).get(id)
    if not obj: raise HTTPException(404, "Register not found")
    return obj


@router.get("/admissions")
def list_admissions(register_id: Optional[int] = None, state: Optional[str] = None,
                    skip: int = 0, limit: int = 100,
                    db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpAdmission)
    if register_id: q = q.filter_by(register_id=register_id)
    if state: q = q.filter_by(state=state)
    return {"total": q.count(), "items": q.offset(skip).limit(limit).all()}

@router.post("/admissions", status_code=201)
def create_admission(first_name: str, last_name: str, register_id: int,
                     birth_date: Optional[date] = None, gender: Optional[str] = None,
                     email: Optional[str] = None, phone: Optional[str] = None,
                     db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = OpAdmission(first_name=first_name, last_name=last_name, register_id=register_id,
                      birth_date=birth_date, gender=gender, email=email, phone=phone)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/admissions/{id}")
def get_admission(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpAdmission).get(id)
    if not obj: raise HTTPException(404, "Admission not found")
    return obj

@router.patch("/admissions/{id}/state")
def update_admission_state(id: int, state: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpAdmission).get(id)
    if not obj: raise HTTPException(404, "Admission not found")
    obj.state = state
    db.commit(); db.refresh(obj); return obj
