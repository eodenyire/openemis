from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin, require_teacher
from app.api.crud import get_one, get_all, create_obj, update_obj, delete_obj
from app.models.exam import ExamSession, Exam, ExamAttendees, GradingConfig, GradingRule
from app.schemas.exam import (
    ExamSessionCreate, ExamSessionUpdate, ExamSessionOut,
    ExamCreate, ExamUpdate, ExamOut,
    ExamAttendeeCreate, ExamAttendeeUpdate, ExamAttendeeOut,
    GradingConfigCreate, GradingConfigUpdate, GradingConfigOut,
)

router = APIRouter()


# ── Exam Sessions ─────────────────────────────────────────────────────────────
@router.get("/sessions/", response_model=List[ExamSessionOut], tags=["Exams"])
def list_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                  _=Depends(get_current_user)):
    return get_all(db, ExamSession, skip, limit)

@router.post("/sessions/", response_model=ExamSessionOut, status_code=201, tags=["Exams"])
def create_session(data: ExamSessionCreate, db: Session = Depends(get_db),
                   _=Depends(require_teacher)):
    return create_obj(db, ExamSession, data.model_dump())

@router.get("/sessions/{id}", response_model=ExamSessionOut, tags=["Exams"])
def get_session(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, ExamSession, id)
    if not obj: raise HTTPException(404, "Session not found")
    return obj

@router.put("/sessions/{id}", response_model=ExamSessionOut, tags=["Exams"])
def update_session(id: int, data: ExamSessionUpdate, db: Session = Depends(get_db),
                   _=Depends(require_teacher)):
    obj = get_one(db, ExamSession, id)
    if not obj: raise HTTPException(404, "Session not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/sessions/{id}", status_code=204, tags=["Exams"])
def delete_session(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, ExamSession, id)
    if not obj: raise HTTPException(404, "Session not found")
    delete_obj(db, obj)


# ── Exams ─────────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[ExamOut], tags=["Exams"])
def list_exams(skip: int = 0, limit: int = 100, course_id: int = None,
               db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(Exam)
    if course_id:
        q = q.filter(Exam.course_id == course_id)
    return q.offset(skip).limit(limit).all()

@router.post("/", response_model=ExamOut, status_code=201, tags=["Exams"])
def create_exam(data: ExamCreate, db: Session = Depends(get_db),
                _=Depends(require_teacher)):
    if db.query(Exam).filter(Exam.exam_code == data.exam_code).first():
        raise HTTPException(400, "Exam code already exists")
    return create_obj(db, Exam, data.model_dump())

@router.get("/{id}", response_model=ExamOut, tags=["Exams"])
def get_exam(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, Exam, id)
    if not obj: raise HTTPException(404, "Exam not found")
    return obj

@router.put("/{id}", response_model=ExamOut, tags=["Exams"])
def update_exam(id: int, data: ExamUpdate, db: Session = Depends(get_db),
                _=Depends(require_teacher)):
    obj = get_one(db, Exam, id)
    if not obj: raise HTTPException(404, "Exam not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.post("/{id}/schedule", response_model=ExamOut, tags=["Exams"])
def schedule_exam(id: int, db: Session = Depends(get_db), _=Depends(require_teacher)):
    obj = get_one(db, Exam, id)
    if not obj: raise HTTPException(404, "Exam not found")
    return update_obj(db, obj, {"state": "scheduled"})

@router.post("/{id}/hold", response_model=ExamOut, tags=["Exams"])
def hold_exam(id: int, db: Session = Depends(get_db), _=Depends(require_teacher)):
    obj = get_one(db, Exam, id)
    if not obj: raise HTTPException(404, "Exam not found")
    return update_obj(db, obj, {"state": "held"})

@router.post("/{id}/done", response_model=ExamOut, tags=["Exams"])
def done_exam(id: int, db: Session = Depends(get_db), _=Depends(require_teacher)):
    obj = get_one(db, Exam, id)
    if not obj: raise HTTPException(404, "Exam not found")
    return update_obj(db, obj, {"state": "done"})

@router.delete("/{id}", status_code=204, tags=["Exams"])
def delete_exam(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Exam, id)
    if not obj: raise HTTPException(404, "Exam not found")
    delete_obj(db, obj)


# ── Attendees / Results ───────────────────────────────────────────────────────
@router.get("/{exam_id}/attendees", response_model=List[ExamAttendeeOut], tags=["Exams"])
def list_attendees(exam_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(ExamAttendees).filter(ExamAttendees.exam_id == exam_id).all()

@router.post("/{exam_id}/attendees", response_model=ExamAttendeeOut, status_code=201, tags=["Exams"])
def add_attendee(exam_id: int, data: ExamAttendeeCreate, db: Session = Depends(get_db),
                 _=Depends(require_teacher)):
    payload = data.model_dump()
    payload["exam_id"] = exam_id
    return create_obj(db, ExamAttendees, payload)

@router.put("/attendees/{id}", response_model=ExamAttendeeOut, tags=["Exams"])
def update_attendee(id: int, data: ExamAttendeeUpdate, db: Session = Depends(get_db),
                    _=Depends(require_teacher)):
    obj = db.query(ExamAttendees).filter(ExamAttendees.id == id).first()
    if not obj: raise HTTPException(404, "Attendee not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))


# ── Grading Configs ───────────────────────────────────────────────────────────
@router.get("/grading/", response_model=List[GradingConfigOut], tags=["Exams"])
def list_grading(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, GradingConfig)

@router.post("/grading/", response_model=GradingConfigOut, status_code=201, tags=["Exams"])
def create_grading(data: GradingConfigCreate, db: Session = Depends(get_db),
                   _=Depends(require_admin)):
    rules = data.rules or []
    config = create_obj(db, GradingConfig, {"name": data.name})
    for rule in rules:
        create_obj(db, GradingRule, {**rule.model_dump(), "config_id": config.id})
    db.refresh(config)
    return config

@router.get("/grading/{id}", response_model=GradingConfigOut, tags=["Exams"])
def get_grading(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, GradingConfig, id)
    if not obj: raise HTTPException(404, "Grading config not found")
    return obj
