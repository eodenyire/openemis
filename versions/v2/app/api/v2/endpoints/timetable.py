"""Timetable endpoints."""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.timetable import OpClassroom, OpTiming, OpSession

router = APIRouter()


@router.get("/classrooms")
def list_classrooms(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpClassroom).filter_by(active=True).all()

@router.post("/classrooms", status_code=201)
def create_classroom(name: str, capacity: int = 0, building: Optional[str] = None,
                     db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpClassroom(name=name, capacity=capacity, building=building)
    db.add(obj); db.commit(); db.refresh(obj); return obj


@router.get("/timings")
def list_timings(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpTiming).all()

@router.post("/timings", status_code=201)
def create_timing(name: str, start_time: str, end_time: str,
                  db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpTiming(name=name, start_time=start_time, end_time=end_time)
    db.add(obj); db.commit(); db.refresh(obj); return obj


@router.get("/sessions")
def list_sessions(course_id: Optional[int] = None, batch_id: Optional[int] = None,
                  faculty_id: Optional[int] = None, skip: int = 0, limit: int = 100,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpSession).filter_by(active=True)
    if course_id: q = q.filter_by(course_id=course_id)
    if batch_id: q = q.filter_by(batch_id=batch_id)
    if faculty_id: q = q.filter_by(faculty_id=faculty_id)
    return {"total": q.count(), "items": q.offset(skip).limit(limit).all()}

@router.post("/sessions", status_code=201)
def create_session(course_id: int, faculty_id: int, batch_id: int, subject_id: int,
                   start_datetime: datetime, end_datetime: datetime,
                   classroom_id: Optional[int] = None, timing_id: Optional[int] = None,
                   days: Optional[str] = None,
                   db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpSession(course_id=course_id, faculty_id=faculty_id, batch_id=batch_id,
                    subject_id=subject_id, start_datetime=start_datetime, end_datetime=end_datetime,
                    classroom_id=classroom_id, timing_id=timing_id, days=days)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/sessions/{id}")
def get_session(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpSession).get(id)
    if not obj: raise HTTPException(404, "Session not found")
    return obj

@router.patch("/sessions/{id}/state")
def update_session_state(id: int, state: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpSession).get(id)
    if not obj: raise HTTPException(404, "Session not found")
    obj.state = state
    db.commit(); db.refresh(obj); return obj
