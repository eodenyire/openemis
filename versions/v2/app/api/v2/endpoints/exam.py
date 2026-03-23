"""Exam endpoints."""
from typing import Optional, List
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.exam import (
    OpExamSession, OpExam, OpExamAttendee,
    OpMarksheetRegister, OpMarksheetLine, OpGradingConfig, OpGradingRule,
)

router = APIRouter()


class MarkEntry(BaseModel):
    student_id: int
    marks: float


# ── Exam Sessions ─────────────────────────────────────────────────────────────
@router.get("/exam-sessions")
def list_exam_sessions(course_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpExamSession).filter_by(active=True)
    if course_id: q = q.filter_by(course_id=course_id)
    return q.all()

@router.post("/exam-sessions", status_code=201)
def create_exam_session(name: str, course_id: int, batch_id: Optional[int] = None,
                        academic_year_id: Optional[int] = None,
                        start_date: Optional[date] = None, end_date: Optional[date] = None,
                        db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpExamSession(name=name, course_id=course_id, batch_id=batch_id,
                        academic_year_id=academic_year_id, start_date=start_date, end_date=end_date)
    db.add(obj); db.commit(); db.refresh(obj); return obj


# ── Exams ─────────────────────────────────────────────────────────────────────
@router.get("/exams")
def list_exams(session_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpExam).filter_by(active=True)
    if session_id: q = q.filter_by(session_id=session_id)
    return q.all()

@router.post("/exams", status_code=201)
def create_exam(name: str, exam_code: str, subject_id: int, total_marks: int, min_marks: int,
                start_time: datetime, end_time: datetime, session_id: Optional[int] = None,
                db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(OpExam).filter_by(exam_code=exam_code).first():
        raise HTTPException(409, "Exam code already exists")
    obj = OpExam(name=name, exam_code=exam_code, subject_id=subject_id, total_marks=total_marks,
                 min_marks=min_marks, start_time=start_time, end_time=end_time, session_id=session_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/exams/{id}")
def get_exam(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpExam).get(id)
    if not obj: raise HTTPException(404, "Exam not found")
    return obj

@router.post("/exams/{id}/marks", status_code=201)
def enter_marks(id: int, entries: List[MarkEntry], db: Session = Depends(get_db), _=Depends(require_admin)):
    exam = db.query(OpExam).get(id)
    if not exam: raise HTTPException(404, "Exam not found")
    for entry in entries:
        attendee = db.query(OpExamAttendee).filter_by(exam_id=id, student_id=entry.student_id).first()
        if attendee:
            attendee.marks = entry.marks
            attendee.status = "pass" if entry.marks >= exam.min_marks else "fail"
        else:
            db.add(OpExamAttendee(exam_id=id, student_id=entry.student_id, marks=entry.marks,
                                   status="pass" if entry.marks >= exam.min_marks else "fail"))
    db.commit()
    return {"message": f"{len(entries)} marks saved"}

@router.get("/exams/{id}/marks")
def get_marks(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpExamAttendee).filter_by(exam_id=id).all()


# ── Marksheets ────────────────────────────────────────────────────────────────
@router.get("/marksheets")
def list_marksheets(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpMarksheetRegister).all()

@router.post("/marksheets", status_code=201)
def create_marksheet(exam_session_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpMarksheetRegister(exam_session_id=exam_session_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj


# ── Grading ───────────────────────────────────────────────────────────────────
@router.get("/grading-configs")
def list_grading_configs(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpGradingConfig).filter_by(active=True).all()

@router.post("/grading-configs", status_code=201)
def create_grading_config(name: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpGradingConfig(name=name)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.post("/grading-configs/{id}/rules", status_code=201)
def add_grading_rule(id: int, name: str, min_marks: float, max_marks: float, gpa_point: float = 0,
                     db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpGradingRule(config_id=id, name=name, min_marks=min_marks, max_marks=max_marks, gpa_point=gpa_point)
    db.add(obj); db.commit(); db.refresh(obj); return obj
