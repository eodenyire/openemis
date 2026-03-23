"""Events & Calendar endpoints."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.extras import Event, EventType, EventRegistration

router = APIRouter()


class EventTypeCreate(BaseModel):
    name: str

class EventCreate(BaseModel):
    name: str
    event_type_id: Optional[int] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    max_participants: Optional[int] = None

class EventUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    max_participants: Optional[int] = None

class RegistrationCreate(BaseModel):
    student_id: int


# ── Event Types ───────────────────────────────────────────────────────────────

@router.get("/types")
def list_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(EventType).all()

@router.post("/types", status_code=201)
def create_type(data: EventTypeCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = EventType(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# ── Events ────────────────────────────────────────────────────────────────────

@router.get("/")
def list_events(
    upcoming_only: bool = False,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(Event).filter_by(active=True)
    if upcoming_only:
        q = q.filter(Event.start_date >= datetime.utcnow())
    total = q.count()
    items = q.order_by(Event.start_date).offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": e.id, "name": e.name, "start_date": e.start_date,
         "end_date": e.end_date, "location": e.location,
         "event_type": e.event_type.name if e.event_type else None,
         "max_participants": e.max_participants,
         "registered": len(e.registrations)}
        for e in items
    ]}

@router.post("/", status_code=201)
def create_event(data: EventCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = Event(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "name": obj.name, "start_date": obj.start_date}

@router.get("/{id}")
def get_event(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Event).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Event not found")
    return {"id": obj.id, "name": obj.name, "start_date": obj.start_date,
            "end_date": obj.end_date, "location": obj.location,
            "description": obj.description, "max_participants": obj.max_participants,
            "registrations": [
                {"student_id": r.student_id, "status": r.status}
                for r in obj.registrations
            ]}

@router.put("/{id}")
def update_event(id: int, data: EventUpdate, db: Session = Depends(get_db),
                 _=Depends(get_current_user)):
    obj = db.query(Event).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Event not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "name": obj.name}

@router.delete("/{id}", status_code=204)
def delete_event(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Event).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Event not found")
    obj.active = False; db.commit()


# ── Registrations ─────────────────────────────────────────────────────────────

@router.post("/{id}/register", status_code=201)
def register_student(id: int, data: RegistrationCreate,
                     db: Session = Depends(get_db), _=Depends(get_current_user)):
    event = db.query(Event).filter_by(id=id, active=True).first()
    if not event: raise HTTPException(404, "Event not found")
    existing = db.query(EventRegistration).filter_by(
        event_id=id, student_id=data.student_id).first()
    if existing: raise HTTPException(400, "Already registered")
    if event.max_participants and len(event.registrations) >= event.max_participants:
        raise HTTPException(400, "Event is full")
    reg = EventRegistration(event_id=id, student_id=data.student_id)
    db.add(reg); db.commit(); db.refresh(reg)
    return {"id": reg.id, "event_id": id, "student_id": data.student_id, "status": reg.status}

@router.put("/{id}/registrations/{reg_id}")
def update_registration(id: int, reg_id: int, status: str,
                        db: Session = Depends(get_db), _=Depends(get_current_user)):
    reg = db.query(EventRegistration).filter_by(id=reg_id, event_id=id).first()
    if not reg: raise HTTPException(404, "Registration not found")
    reg.status = status; db.commit()
    return {"id": reg.id, "status": reg.status}
