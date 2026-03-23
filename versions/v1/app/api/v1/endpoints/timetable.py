from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin, require_teacher
from app.api.crud import get_one, get_all, create_obj, update_obj, delete_obj
from app.models.timetable import Timing, Classroom, Session as TimetableSession
from app.schemas.timetable import (
    TimingCreate, TimingUpdate, TimingOut,
    ClassroomCreate, ClassroomUpdate, ClassroomOut,
    SessionCreate, SessionUpdate, SessionOut,
)

router = APIRouter()

# ── Timings ───────────────────────────────────────────────────────────────────
@router.get("/timings", response_model=List[TimingOut], tags=["Timetable"])
def list_timings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, Timing, skip, limit)

@router.post("/timings", response_model=TimingOut, status_code=201, tags=["Timetable"])
def create_timing(data: TimingCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, Timing, data.model_dump())

@router.get("/timings/{id}", response_model=TimingOut, tags=["Timetable"])
def get_timing(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, Timing, id)
    if not obj: raise HTTPException(404, "Timing not found")
    return obj

@router.put("/timings/{id}", response_model=TimingOut, tags=["Timetable"])
def update_timing(id: int, data: TimingUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Timing, id)
    if not obj: raise HTTPException(404, "Timing not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/timings/{id}", status_code=204, tags=["Timetable"])
def delete_timing(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Timing, id)
    if not obj: raise HTTPException(404, "Timing not found")
    delete_obj(db, obj)


# ── Classrooms ────────────────────────────────────────────────────────────────
@router.get("/classrooms", response_model=List[ClassroomOut], tags=["Timetable"])
def list_classrooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, Classroom, skip, limit)

@router.post("/classrooms", response_model=ClassroomOut, status_code=201, tags=["Timetable"])
def create_classroom(data: ClassroomCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, Classroom, data.model_dump())

@router.get("/classrooms/{id}", response_model=ClassroomOut, tags=["Timetable"])
def get_classroom(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, Classroom, id)
    if not obj: raise HTTPException(404, "Classroom not found")
    return obj

@router.put("/classrooms/{id}", response_model=ClassroomOut, tags=["Timetable"])
def update_classroom(id: int, data: ClassroomUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Classroom, id)
    if not obj: raise HTTPException(404, "Classroom not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/classrooms/{id}", status_code=204, tags=["Timetable"])
def delete_classroom(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Classroom, id)
    if not obj: raise HTTPException(404, "Classroom not found")
    delete_obj(db, obj)


# ── Sessions ──────────────────────────────────────────────────────────────────
@router.get("/sessions", response_model=List[SessionOut], tags=["Timetable"])
def list_sessions(skip: int = 0, limit: int = 100, course_id: int = None,
                  batch_id: int = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(TimetableSession)
    if course_id: q = q.filter(TimetableSession.course_id == course_id)
    if batch_id: q = q.filter(TimetableSession.batch_id == batch_id)
    return q.offset(skip).limit(limit).all()

@router.post("/sessions", response_model=SessionOut, status_code=201, tags=["Timetable"])
def create_session(data: SessionCreate, db: Session = Depends(get_db), _=Depends(require_teacher)):
    return create_obj(db, TimetableSession, data.model_dump())

@router.get("/sessions/{id}", response_model=SessionOut, tags=["Timetable"])
def get_session(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, TimetableSession, id)
    if not obj: raise HTTPException(404, "Session not found")
    return obj

@router.put("/sessions/{id}", response_model=SessionOut, tags=["Timetable"])
def update_session(id: int, data: SessionUpdate, db: Session = Depends(get_db), _=Depends(require_teacher)):
    obj = get_one(db, TimetableSession, id)
    if not obj: raise HTTPException(404, "Session not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/sessions/{id}", status_code=204, tags=["Timetable"])
def delete_session(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, TimetableSession, id)
    if not obj: raise HTTPException(404, "Session not found")
    delete_obj(db, obj)
