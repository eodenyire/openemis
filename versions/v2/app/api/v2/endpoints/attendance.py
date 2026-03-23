"""Attendance endpoints."""
from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.attendance import OpAttendanceRegister, OpAttendanceSheet, OpAttendanceLine

router = APIRouter()


class AttendanceLineIn(BaseModel):
    student_id: int
    present: bool = False
    absent: bool = False
    excused: bool = False
    late: bool = False
    remark: Optional[str] = None


@router.get("/attendance-registers")
def list_registers(course_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpAttendanceRegister).filter_by(active=True)
    if course_id: q = q.filter_by(course_id=course_id)
    return q.all()

@router.post("/attendance-registers", status_code=201)
def create_register(name: str, course_id: int, batch_id: Optional[int] = None,
                    academic_year_id: Optional[int] = None,
                    db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpAttendanceRegister(name=name, course_id=course_id, batch_id=batch_id,
                                academic_year_id=academic_year_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj


@router.get("/attendance-sheets")
def list_sheets(register_id: Optional[int] = None, attendance_date: Optional[date] = None,
                db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpAttendanceSheet).filter_by(active=True)
    if register_id: q = q.filter_by(register_id=register_id)
    if attendance_date: q = q.filter_by(attendance_date=attendance_date)
    return q.all()

@router.post("/attendance-sheets", status_code=201)
def create_sheet(register_id: int, attendance_date: date, faculty_id: Optional[int] = None,
                 session_id: Optional[int] = None,
                 db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpAttendanceSheet(register_id=register_id, attendance_date=attendance_date,
                             faculty_id=faculty_id, session_id=session_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/attendance-sheets/{id}")
def get_sheet(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpAttendanceSheet).get(id)
    if not obj: raise HTTPException(404, "Sheet not found")
    return obj

@router.post("/attendance-sheets/{id}/lines", status_code=201)
def submit_attendance(id: int, lines: List[AttendanceLineIn],
                      db: Session = Depends(get_db), _=Depends(require_admin)):
    sheet = db.query(OpAttendanceSheet).get(id)
    if not sheet: raise HTTPException(404, "Sheet not found")
    # Remove existing lines and re-insert
    db.query(OpAttendanceLine).filter_by(sheet_id=id).delete()
    for line in lines:
        db.add(OpAttendanceLine(sheet_id=id, **line.dict()))
    sheet.state = "done"
    db.commit()
    return {"message": f"{len(lines)} attendance lines saved"}

@router.get("/attendance-sheets/{id}/lines")
def get_sheet_lines(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpAttendanceLine).filter_by(sheet_id=id).all()
