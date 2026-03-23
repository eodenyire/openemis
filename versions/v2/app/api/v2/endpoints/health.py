"""Health records endpoints."""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.support import OpHealthRecord

router = APIRouter()


@router.get("/health/records")
def list_records(student_id: Optional[int] = None, skip: int = 0, limit: int = 100,
                 db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpHealthRecord).filter_by(active=True)
    if student_id: q = q.filter_by(student_id=student_id)
    return {"total": q.count(), "items": q.offset(skip).limit(limit).all()}

@router.post("/health/records", status_code=201)
def create_record(student_id: int, visit_date: date,
                  complaint: Optional[str] = None, diagnosis: Optional[str] = None,
                  treatment: Optional[str] = None, doctor: Optional[str] = None,
                  follow_up_date: Optional[date] = None,
                  db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpHealthRecord(student_id=student_id, visit_date=visit_date, complaint=complaint,
                         diagnosis=diagnosis, treatment=treatment, doctor=doctor,
                         follow_up_date=follow_up_date)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/health/records/{id}")
def get_record(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpHealthRecord).get(id)
    if not obj: raise HTTPException(404, "Record not found")
    return obj

@router.put("/health/records/{id}")
def update_record(id: int, complaint: Optional[str] = None, diagnosis: Optional[str] = None,
                  treatment: Optional[str] = None, follow_up_date: Optional[date] = None,
                  db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpHealthRecord).get(id)
    if not obj: raise HTTPException(404, "Record not found")
    if complaint is not None: obj.complaint = complaint
    if diagnosis is not None: obj.diagnosis = diagnosis
    if treatment is not None: obj.treatment = treatment
    if follow_up_date is not None: obj.follow_up_date = follow_up_date
    db.commit(); db.refresh(obj); return obj
