"""Activity, Achievement, Discipline endpoints."""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.extras import OpActivity, OpAchievement, OpDisciplineRecord

router = APIRouter()


# ── Activities ────────────────────────────────────────────────────────────────
@router.get("/activities")
def list_activities(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpActivity).filter_by(active=True).all()

@router.post("/activities", status_code=201)
def create_activity(name: str, activity_type: Optional[str] = None,
                    description: Optional[str] = None,
                    start_date: Optional[date] = None, end_date: Optional[date] = None,
                    responsible_id: Optional[int] = None,
                    db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpActivity(name=name, activity_type=activity_type, description=description,
                     start_date=start_date, end_date=end_date, responsible_id=responsible_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/activities/{id}")
def get_activity(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpActivity).get(id)
    if not obj: raise HTTPException(404, "Activity not found")
    return obj

@router.delete("/activities/{id}", status_code=204)
def delete_activity(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpActivity).get(id)
    if not obj: raise HTTPException(404, "Activity not found")
    obj.active = False
    db.commit()


# ── Achievements ──────────────────────────────────────────────────────────────
@router.get("/achievements")
def list_achievements(student_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpAchievement).filter_by(active=True)
    if student_id: q = q.filter_by(student_id=student_id)
    return q.all()

@router.post("/achievements", status_code=201)
def create_achievement(student_id: int, name: str, achievement_type: Optional[str] = None,
                       date_achieved: Optional[date] = None, description: Optional[str] = None,
                       db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpAchievement(student_id=student_id, name=name, achievement_type=achievement_type,
                        date=date_achieved, description=description)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/achievements/{id}")
def get_achievement(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpAchievement).get(id)
    if not obj: raise HTTPException(404, "Achievement not found")
    return obj


# ── Discipline ────────────────────────────────────────────────────────────────
@router.get("/discipline")
def list_discipline(student_id: Optional[int] = None, state: Optional[str] = None,
                    db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpDisciplineRecord).filter_by(active=True)
    if student_id: q = q.filter_by(student_id=student_id)
    if state: q = q.filter_by(state=state)
    return q.all()

@router.post("/discipline", status_code=201)
def create_discipline_record(student_id: int, incident_date: date,
                              incident_type: Optional[str] = None, description: Optional[str] = None,
                              action_taken: Optional[str] = None, reported_by_id: Optional[int] = None,
                              db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpDisciplineRecord(student_id=student_id, incident_date=incident_date,
                              incident_type=incident_type, description=description,
                              action_taken=action_taken, reported_by_id=reported_by_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.patch("/discipline/{id}/resolve")
def resolve_case(id: int, action_taken: Optional[str] = None,
                 db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpDisciplineRecord).get(id)
    if not obj: raise HTTPException(404, "Record not found")
    obj.state = "closed"
    if action_taken: obj.action_taken = action_taken
    db.commit(); db.refresh(obj); return obj
