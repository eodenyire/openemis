"""Scholarships endpoints."""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.extras import OpScholarship, OpScholarshipAward

router = APIRouter()


@router.get("/scholarships")
def list_scholarships(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpScholarship).filter_by(active=True).all()

@router.post("/scholarships", status_code=201)
def create_scholarship(name: str, scholarship_type: Optional[str] = None,
                       amount: float = 0, criteria: Optional[str] = None,
                       db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpScholarship(name=name, scholarship_type=scholarship_type, amount=amount, criteria=criteria)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/scholarships/{id}")
def get_scholarship(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpScholarship).get(id)
    if not obj: raise HTTPException(404, "Scholarship not found")
    return obj


@router.get("/scholarship-awards")
def list_awards(student_id: Optional[int] = None, scholarship_id: Optional[int] = None,
                db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpScholarshipAward)
    if student_id: q = q.filter_by(student_id=student_id)
    if scholarship_id: q = q.filter_by(scholarship_id=scholarship_id)
    return q.all()

@router.post("/scholarship-awards", status_code=201)
def award_scholarship(scholarship_id: int, student_id: int, amount: float,
                      academic_year_id: Optional[int] = None, award_date: Optional[date] = None,
                      db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpScholarshipAward(scholarship_id=scholarship_id, student_id=student_id, amount=amount,
                              academic_year_id=academic_year_id, award_date=award_date or date.today())
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.patch("/scholarship-awards/{id}/confirm")
def confirm_award(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpScholarshipAward).get(id)
    if not obj: raise HTTPException(404, "Award not found")
    obj.state = "confirmed"
    db.commit(); db.refresh(obj); return obj
