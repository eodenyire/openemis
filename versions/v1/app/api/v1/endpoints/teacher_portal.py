"""
Teacher Portal — role-scoped dashboard for teachers.
Shows their classes, timetable, attendance sheets, assignments, exam results.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.people import Teacher, StudentCourse
from app.models.attendance import AttendanceRegister, AttendanceSheet, AttendanceLine, AttendanceStatus
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.exam import Exam, ExamAttendees
from app.models.lms import TimetableSlot

router = APIRouter()


def _get_teacher(db: Session, user_id: int) -> Teacher:
    teacher = db.query(Teacher).filter_by(user_id=user_id, active=True).first()
    if not teacher:
        raise HTTPException(403, "Teacher profile not found for this user")
    return teacher


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard")
def teacher_dashboard(db: Session = Depends(get_db),
                      current_user=Depends(get_current_user)):
    teacher = _get_teacher(db, current_user.id)

    # Classes taught (via timetable slots)
    timetable_entries = db.query(TimetableSlot).filter_by(
        teacher_id=teacher.id, is_active=True).all()
    course_ids = list({t.course_id for t in timetable_entries if t.course_id})

    # Attendance registers owned by this teacher
    registers = db.query(AttendanceRegister).filter_by(active=True).all()
    my_registers = [r for r in registers if any(
        s.faculty_id == teacher.id for s in r.sheets)]

    # Pending assignments to mark
    pending_assignments = (db.query(Assignment)
                           .filter_by(faculty_id=teacher.id, active=True).count())

    # Upcoming exams (for teacher's courses)
    slot_course_ids = [
        s.course_id for s in
        db.query(TimetableSlot).filter_by(teacher_id=teacher.id, is_active=True).all()
    ]
    from datetime import datetime
    upcoming_exams = (db.query(Exam)
                      .filter(Exam.course_id.in_(slot_course_ids))
                      .filter(Exam.start_time >= datetime.utcnow())
                      .filter(Exam.active == True).count())

    return {
        "teacher_id": teacher.id,
        "name": f"{teacher.first_name} {teacher.last_name}",
        "employee_id": teacher.employee_id,
        "subjects": [s.name for s in teacher.subjects],
        "classes_count": len(course_ids),
        "pending_assignments": pending_assignments,
        "upcoming_exams": upcoming_exams,
        "attendance_registers": len(my_registers),
    }


# ── My Classes ────────────────────────────────────────────────────────────────

@router.get("/classes")
def my_classes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    teacher = _get_teacher(db, current_user.id)
    entries = db.query(TimetableSlot).filter_by(teacher_id=teacher.id, is_active=True).all()
    seen = set()
    classes = []
    for e in entries:
        if e.course_id and e.course_id not in seen:
            seen.add(e.course_id)
            student_count = db.query(StudentCourse).filter_by(
                course_id=e.course_id, state="running").count()
            classes.append({
                "course_id": e.course_id,
                "course_name": e.course.name if e.course else None,
                "student_count": student_count,
            })
    return classes


# ── My Timetable ──────────────────────────────────────────────────────────────

@router.get("/timetable")
def my_timetable(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    teacher = _get_teacher(db, current_user.id)
    entries = (db.query(TimetableSlot)
               .filter_by(teacher_id=teacher.id, is_active=True)
               .order_by(TimetableSlot.day_of_week, TimetableSlot.timing_id).all())
    return [
        {"id": e.id, "day": e.day_of_week,
         "start_time": str(e.timing.start_time) if e.timing else None,
         "end_time": str(e.timing.end_time) if e.timing else None,
         "course": e.course.name if e.course else None,
         "subject": e.subject.name if e.subject else None,
         "room": e.classroom.name if e.classroom else None}
        for e in entries
    ]


# ── Attendance ────────────────────────────────────────────────────────────────

@router.get("/attendance/sheets")
def my_attendance_sheets(
    course_id: Optional[int] = None,
    skip: int = 0, limit: int = 30,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    teacher = _get_teacher(db, current_user.id)
    q = db.query(AttendanceSheet).filter_by(faculty_id=teacher.id)
    if course_id:
        q = q.join(AttendanceRegister).filter(AttendanceRegister.course_id == course_id)
    total = q.count()
    sheets = q.order_by(AttendanceSheet.attendance_date.desc()).offset(skip).limit(limit).all()
    return {"total": total, "sheets": [
        {"id": s.id, "date": s.attendance_date, "state": s.state,
         "register_id": s.register_id,
         "lines_count": len(s.lines)}
        for s in sheets
    ]}

@router.get("/attendance/sheets/{sheet_id}")
def get_sheet_lines(sheet_id: int, db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):
    teacher = _get_teacher(db, current_user.id)
    sheet = db.query(AttendanceSheet).filter_by(id=sheet_id, faculty_id=teacher.id).first()
    if not sheet: raise HTTPException(404, "Sheet not found or not yours")
    return {
        "sheet_id": sheet.id, "date": sheet.attendance_date, "state": sheet.state,
        "lines": [
            {"id": l.id, "student_id": l.student_id,
             "student_name": f"{l.student.first_name} {l.student.last_name}" if l.student else None,
             "status": l.status, "note": l.note}
            for l in sheet.lines
        ]
    }


# ── Assignments ───────────────────────────────────────────────────────────────

@router.get("/assignments")
def my_assignments(
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    teacher = _get_teacher(db, current_user.id)
    q = db.query(Assignment).filter_by(faculty_id=teacher.id, active=True)
    total = q.count()
    items = q.order_by(Assignment.submission_date.desc()).offset(skip).limit(limit).all()
    return {"total": total, "assignments": [
        {"id": a.id, "name": a.name,
         "course": a.course.name if a.course else None,
         "subject": a.subject.name if a.subject else None,
         "deadline": a.submission_date, "total_marks": a.total_marks,
         "submissions": db.query(AssignmentSubmission).filter_by(assignment_id=a.id).count()}
        for a in items
    ]}

@router.get("/assignments/{assignment_id}/submissions")
def assignment_submissions(assignment_id: int, db: Session = Depends(get_db),
                           current_user=Depends(get_current_user)):
    teacher = _get_teacher(db, current_user.id)
    assignment = db.query(Assignment).filter_by(
        id=assignment_id, faculty_id=teacher.id).first()
    if not assignment: raise HTTPException(404, "Assignment not found or not yours")
    subs = db.query(AssignmentSubmission).filter_by(assignment_id=assignment_id).all()
    return [
        {"id": s.id, "student_id": s.student_id,
         "student_name": f"{s.student.first_name} {s.student.last_name}" if s.student else None,
         "submission_date": s.submission_date,
         "marks": s.marks, "state": s.state, "feedback": s.feedback}
        for s in subs
    ]


# ── Exams ─────────────────────────────────────────────────────────────────────

@router.get("/exams")
def my_exams(
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    teacher = _get_teacher(db, current_user.id)
    # Get exams for courses this teacher teaches
    slot_course_ids = [
        s.course_id for s in
        db.query(TimetableSlot).filter_by(teacher_id=teacher.id, is_active=True).all()
    ]
    q = db.query(Exam).filter(Exam.course_id.in_(slot_course_ids), Exam.active == True)
    total = q.count()
    items = q.order_by(Exam.start_time.desc()).offset(skip).limit(limit).all()
    return {"total": total, "exams": [
        {"id": e.id, "name": e.name,
         "course": e.course.name if e.course else None,
         "subject": e.subject.name if e.subject else None,
         "start_time": e.start_time, "total_marks": e.total_marks,
         "attendees": db.query(ExamAttendees).filter_by(exam_id=e.id).count()}
        for e in items
    ]}
