"""Discipline module endpoints."""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.extras import Discipline, DisciplineAction

router = APIRouter()


class ActionCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DisciplineCreate(BaseModel):
    student_id: int
    date: date
    description: str
    action_id: Optional[int] = None
    severity: str = "minor"

class DisciplineUpdate(BaseModel):
    description: Optional[str] = None
    action_id: Optional[int] = None
    severity: Optional[str] = None


# ── Actions ───────────────────────────────────────────────────────────────────

@router.get("/actions")
def list_actions(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(DisciplineAction).all()

@router.post("/actions", status_code=201)
def create_action(data: ActionCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = DisciplineAction(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# ── Records ───────────────────────────────────────────────────────────────────

@router.get("/")
def list_records(
    student_id: Optional[int] = None,
    severity: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(Discipline).filter_by(active=True)
    if student_id: q = q.filter_by(student_id=student_id)
    if severity: q = q.filter_by(severity=severity)
    total = q.count()
    items = q.order_by(Discipline.date.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": r.id, "student_id": r.student_id, "date": r.date,
         "description": r.description, "severity": r.severity,
         "action": r.action.name if r.action else None,
         "reported_by": r.reported_by, "created_at": r.created_at}
        for r in items
    ]}

@router.post("/", status_code=201)
def create_record(data: DisciplineCreate, db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    obj = Discipline(**data.model_dump(), reported_by=current_user.id)
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "student_id": obj.student_id, "severity": obj.severity}

@router.get("/{id}")
def get_record(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Discipline).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Record not found")
    return {"id": obj.id, "student_id": obj.student_id, "date": obj.date,
            "description": obj.description, "severity": obj.severity,
            "action": obj.action.name if obj.action else None,
            "reported_by": obj.reported_by, "created_at": obj.created_at}

@router.put("/{id}")
def update_record(id: int, data: DisciplineUpdate, db: Session = Depends(get_db),
                  _=Depends(get_current_user)):
    obj = db.query(Discipline).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Record not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "severity": obj.severity}

@router.delete("/{id}", status_code=204)
def delete_record(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Discipline).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Record not found")
    obj.active = False
    db.commit()
