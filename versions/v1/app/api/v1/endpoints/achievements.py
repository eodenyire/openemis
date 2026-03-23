"""Achievements & Activities endpoints."""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.extras import (
    Achievement, AchievementType,
    Activity, ActivityType,
)

router = APIRouter()


# ── Achievement Types ─────────────────────────────────────────────────────────

@router.get("/types")
def list_achievement_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(AchievementType).all()

@router.post("/types", status_code=201)
def create_achievement_type(name: str, description: Optional[str] = None,
                             db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = AchievementType(name=name, description=description)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# ── Achievements ──────────────────────────────────────────────────────────────

class AchievementCreate(BaseModel):
    student_id: int
    achievement_type_id: Optional[int] = None
    title: str
    date: Optional[date] = None
    description: Optional[str] = None
    certificate_number: Optional[str] = None

@router.get("/")
def list_achievements(
    student_id: Optional[int] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(Achievement).filter_by(active=True)
    if student_id: q = q.filter_by(student_id=student_id)
    total = q.count()
    items = q.order_by(Achievement.date.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": a.id, "student_id": a.student_id, "title": a.title,
         "date": a.date, "type": a.achievement_type.name if a.achievement_type else None,
         "certificate_number": a.certificate_number, "description": a.description}
        for a in items
    ]}

@router.post("/", status_code=201)
def create_achievement(data: AchievementCreate, db: Session = Depends(get_db),
                       _=Depends(get_current_user)):
    obj = Achievement(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "student_id": obj.student_id, "title": obj.title}

@router.get("/{id}")
def get_achievement(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Achievement).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Achievement not found")
    return {"id": obj.id, "student_id": obj.student_id, "title": obj.title,
            "date": obj.date, "description": obj.description,
            "certificate_number": obj.certificate_number,
            "type": obj.achievement_type.name if obj.achievement_type else None}

@router.delete("/{id}", status_code=204)
def delete_achievement(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Achievement).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Achievement not found")
    obj.active = False; db.commit()


# ── Activity Types ────────────────────────────────────────────────────────────

@router.get("/activity-types")
def list_activity_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(ActivityType).all()

@router.post("/activity-types", status_code=201)
def create_activity_type(name: str, description: Optional[str] = None,
                          db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = ActivityType(name=name, description=description)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# ── Activities ────────────────────────────────────────────────────────────────

class ActivityCreate(BaseModel):
    student_id: int
    activity_type_id: Optional[int] = None
    name: str
    date: Optional[date] = None
    description: Optional[str] = None

@router.get("/activities")
def list_activities(
    student_id: Optional[int] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(Activity).filter_by(active=True)
    if student_id: q = q.filter_by(student_id=student_id)
    total = q.count()
    items = q.order_by(Activity.date.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": a.id, "student_id": a.student_id, "name": a.name,
         "date": a.date, "status": a.status,
         "type": a.activity_type.name if a.activity_type else None}
        for a in items
    ]}

@router.post("/activities", status_code=201)
def create_activity(data: ActivityCreate, db: Session = Depends(get_db),
                    _=Depends(get_current_user)):
    obj = Activity(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "student_id": obj.student_id, "name": obj.name}

@router.delete("/activities/{id}", status_code=204)
def delete_activity(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Activity).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Activity not found")
    obj.active = False; db.commit()
