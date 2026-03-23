"""Timetable v2 — TimetableSlot + Academic Calendar endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from app.db.session import get_db
from app.api.deps import get_current_user, require_teacher
from app.models.lms import TimetableSlot, AcademicCalendarEvent, CalendarEventType

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class SlotCreate(BaseModel):
    academic_year_id: int
    academic_term_id: int
    course_id: int
    batch_id: int
    subject_id: int
    teacher_id: int
    classroom_id: Optional[int] = None
    timing_id: int
    day_of_week: str  # monday…friday

class SlotOut(BaseModel):
    id: int; course_id: int; batch_id: int; subject_id: int
    teacher_id: int; timing_id: int; day_of_week: str; is_active: bool
    class Config: from_attributes = True

class CalendarEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: str = "other"
    start_date: date
    end_date: date
    is_school_wide: bool = True
    academic_year_id: Optional[int] = None

class CalendarEventOut(BaseModel):
    id: int; title: str; event_type: str
    start_date: date; end_date: date; is_school_wide: bool
    class Config: from_attributes = True

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]


# ── Timetable Slots ───────────────────────────────────────────────────────────

@router.get("/slots", response_model=List[SlotOut])
def list_slots(skip: int = 0, limit: int = 200,
               academic_term_id: Optional[int] = None,
               db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(TimetableSlot).filter_by(is_active=True)
    if academic_term_id: q = q.filter_by(academic_term_id=academic_term_id)
    return q.offset(skip).limit(limit).all()

@router.post("/slots", response_model=SlotOut, status_code=201)
def create_slot(data: SlotCreate, db: Session = Depends(get_db),
                _=Depends(require_teacher)):
    if data.day_of_week.lower() not in DAYS:
        raise HTTPException(400, f"day_of_week must be one of {DAYS}")
    # Check teacher double-booking
    conflict = db.query(TimetableSlot).filter_by(
        teacher_id=data.teacher_id,
        timing_id=data.timing_id,
        day_of_week=data.day_of_week.lower(),
        academic_term_id=data.academic_term_id,
        is_active=True,
    ).first()
    if conflict:
        raise HTTPException(409, "Teacher already has a slot at this time")
    obj = TimetableSlot(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/slots/class/{course_id}", response_model=List[SlotOut])
def class_timetable(course_id: int, academic_term_id: Optional[int] = None,
                    db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(TimetableSlot).filter_by(course_id=course_id, is_active=True)
    if academic_term_id: q = q.filter_by(academic_term_id=academic_term_id)
    return q.order_by(TimetableSlot.day_of_week, TimetableSlot.timing_id).all()

@router.get("/slots/teacher/{teacher_id}", response_model=List[SlotOut])
def teacher_timetable(teacher_id: int, academic_term_id: Optional[int] = None,
                      db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(TimetableSlot).filter_by(teacher_id=teacher_id, is_active=True)
    if academic_term_id: q = q.filter_by(academic_term_id=academic_term_id)
    return q.order_by(TimetableSlot.day_of_week, TimetableSlot.timing_id).all()

@router.delete("/slots/{id}", status_code=204)
def delete_slot(id: int, db: Session = Depends(get_db), _=Depends(require_teacher)):
    obj = db.query(TimetableSlot).get(id)
    if not obj: raise HTTPException(404, "Slot not found")
    obj.is_active = False
    db.commit()

@router.post("/slots/auto-generate")
def auto_generate(academic_year_id: int, academic_term_id: int, course_id: int,
                  batch_id: int, db: Session = Depends(get_db),
                  _=Depends(require_teacher)):
    """
    Simple constraint-based auto-generator.
    Assigns subjects round-robin across Mon-Fri using available timings.
    """
    from app.models.core import Subject, Course
    from app.models.timetable import Timing
    from app.models.people import Teacher

    subjects = db.query(Subject).filter_by(course_id=course_id).all()
    timings = db.query(Timing).limit(8).all()
    if not subjects or not timings:
        raise HTTPException(400, "No subjects or timings found for this course")

    # Delete existing slots for this term/course
    db.query(TimetableSlot).filter_by(
        academic_term_id=academic_term_id, course_id=course_id, batch_id=batch_id
    ).delete()

    created = []
    subject_cycle = subjects * (len(DAYS) * len(timings) // len(subjects) + 1)
    idx = 0
    for day in DAYS:
        for timing in timings:
            subj = subject_cycle[idx % len(subject_cycle)]
            idx += 1
            slot = TimetableSlot(
                academic_year_id=academic_year_id,
                academic_term_id=academic_term_id,
                course_id=course_id,
                batch_id=batch_id,
                subject_id=subj.id,
                teacher_id=subj.teacher_id if hasattr(subj, 'teacher_id') and subj.teacher_id else 1,
                timing_id=timing.id,
                day_of_week=day,
            )
            db.add(slot)
            created.append({"day": day, "timing_id": timing.id, "subject": subj.name})
    db.commit()
    return {"generated": len(created), "slots": created}


# ── Academic Calendar ─────────────────────────────────────────────────────────

@router.get("/calendar", response_model=List[CalendarEventOut])
def list_calendar(skip: int = 0, limit: int = 100,
                  academic_year_id: Optional[int] = None,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(AcademicCalendarEvent)
    if academic_year_id: q = q.filter_by(academic_year_id=academic_year_id)
    return q.order_by(AcademicCalendarEvent.start_date).offset(skip).limit(limit).all()

@router.post("/calendar", response_model=CalendarEventOut, status_code=201)
def create_calendar_event(data: CalendarEventCreate, db: Session = Depends(get_db),
                          _=Depends(require_teacher)):
    obj = AcademicCalendarEvent(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/calendar/{id}", response_model=CalendarEventOut)
def get_calendar_event(id: int, db: Session = Depends(get_db),
                       _=Depends(get_current_user)):
    obj = db.query(AcademicCalendarEvent).get(id)
    if not obj: raise HTTPException(404, "Event not found")
    return obj

@router.delete("/calendar/{id}", status_code=204)
def delete_calendar_event(id: int, db: Session = Depends(get_db),
                          _=Depends(require_teacher)):
    obj = db.query(AcademicCalendarEvent).get(id)
    if not obj: raise HTTPException(404, "Event not found")
    db.delete(obj); db.commit()
