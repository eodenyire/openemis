"""Events endpoints."""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.extras import OpEvent, OpEventRegistration

router = APIRouter()


@router.get("/events")
def list_events(event_type: Optional[str] = None, skip: int = 0, limit: int = 100,
                db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpEvent).filter_by(active=True)
    if event_type: q = q.filter_by(event_type=event_type)
    return {"total": q.count(), "items": q.offset(skip).limit(limit).all()}

@router.post("/events", status_code=201)
def create_event(name: str, event_type: Optional[str] = None,
                 start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                 location: Optional[str] = None, description: Optional[str] = None,
                 max_participants: Optional[int] = None,
                 db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpEvent(name=name, event_type=event_type, start_date=start_date, end_date=end_date,
                  location=location, description=description, max_participants=max_participants)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/events/{id}")
def get_event(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpEvent).get(id)
    if not obj: raise HTTPException(404, "Event not found")
    return obj

@router.delete("/events/{id}", status_code=204)
def delete_event(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpEvent).get(id)
    if not obj: raise HTTPException(404, "Event not found")
    obj.active = False; db.commit()


@router.get("/events/{event_id}/registrations")
def list_registrations(event_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpEventRegistration).filter_by(event_id=event_id).all()

@router.post("/events/{event_id}/registrations", status_code=201)
def register_for_event(event_id: int, student_id: int,
                       db: Session = Depends(get_db), _=Depends(get_current_user)):
    event = db.query(OpEvent).get(event_id)
    if not event: raise HTTPException(404, "Event not found")
    existing = db.query(OpEventRegistration).filter_by(event_id=event_id, student_id=student_id).first()
    if existing: raise HTTPException(409, "Already registered")
    if event.max_participants:
        count = db.query(OpEventRegistration).filter_by(event_id=event_id).count()
        if count >= event.max_participants:
            raise HTTPException(400, "Event is full")
    obj = OpEventRegistration(event_id=event_id, student_id=student_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj
