"""Activities module endpoints."""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.extras import Activity, ActivityType

router = APIRouter()


class TypeCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ActivityCreate(BaseModel):
    student_id: int
    activity_type_id: Optional[int] = None
    name: str
    date: Optional[date] = None
    description: Optional[str] = None
    status: str = "active"


@router.get("/types")
def list_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(ActivityType).all()

@router.post("/types", status_code=201)
def create_type(data: TypeCreate, db: Session = Depends(get_db),
                _=Depends(get_current_user)):
    obj = ActivityType(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.get("/")
def list_activities(student_id: Optional[int] = None,
                    activity_type_id: Optional[int] = None,
                    skip: int = 0, limit: int = 50,
                    db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(Activity).filter_by(active=True)
    if student_id:
        q = q.filter_by(student_id=student_id)
    if activity_type_id:
        q = q.filter_by(activity_type_id=activity_type_id)
    return q.order_by(Activity.date.desc()).offset(skip).limit(limit).all()

@router.post("/", status_code=201)
def create_activity(data: ActivityCreate, db: Session = Depends(get_db),
                    _=Depends(get_current_user)):
    obj = Activity(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/{id}")
def get_activity(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Activity).get(id)
    if not obj: raise HTTPException(404, "Activity not found")
    return obj

@router.put("/{id}")
def update_activity(id: int, data: ActivityCreate, db: Session = Depends(get_db),
                    _=Depends(get_current_user)):
    obj = db.query(Activity).get(id)
    if not obj: raise HTTPException(404, "Activity not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/{id}")
def delete_activity(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Activity).get(id)
    if not obj: raise HTTPException(404, "Activity not found")
    obj.active = False
    db.commit()
    return {"status": "deleted"}
