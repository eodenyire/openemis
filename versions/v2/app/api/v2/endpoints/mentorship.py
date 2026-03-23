"""Mentorship endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.extras import OpMentor, OpMentorshipGroup

router = APIRouter()


@router.get("/mentors")
def list_mentors(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpMentor).filter_by(active=True).all()

@router.post("/mentors", status_code=201)
def create_mentor(faculty_id: int, specialization: Optional[str] = None, max_mentees: int = 10,
                  db: Session = Depends(get_db), _=Depends(require_admin)):
    existing = db.query(OpMentor).filter_by(faculty_id=faculty_id, active=True).first()
    if existing: raise HTTPException(409, "Faculty is already a mentor")
    obj = OpMentor(faculty_id=faculty_id, specialization=specialization, max_mentees=max_mentees)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/mentors/{id}")
def get_mentor(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpMentor).get(id)
    if not obj: raise HTTPException(404, "Mentor not found")
    return obj


@router.get("/mentorship-groups")
def list_groups(mentor_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpMentorshipGroup).filter_by(active=True)
    if mentor_id: q = q.filter_by(mentor_id=mentor_id)
    return q.all()

@router.post("/mentorship-groups", status_code=201)
def create_group(name: str, mentor_id: int, academic_year_id: Optional[int] = None,
                 db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpMentorshipGroup(name=name, mentor_id=mentor_id, academic_year_id=academic_year_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/mentorship-groups/{id}")
def get_group(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpMentorshipGroup).get(id)
    if not obj: raise HTTPException(404, "Group not found")
    return obj
