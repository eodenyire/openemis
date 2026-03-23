"""
Student Portal — role-scoped dashboard for students.
Shows own timetable, attendance, assignments, exam results, fees, CBC progress.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.people import Student, StudentCourse
from app.models.attendance import AttendanceLine, AttendanceSheet, AttendanceStatus
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.exam import Exam, ExamAttendees
from app.models.fees import StudentFeeInvoice
from app.models.lms import TimetableSlot
from app.models.extras import Achievement, Activity, Scholarship

router = APIRouter()


def _get_student(db: Session, user_id: int) -> Student:
    student = db.query(Student).filter_by(user_id=user_id, active=True).first()
    if not student:
        raise HTTPException(403, "Student profile not found for this user")
    return student


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard")
def student_dashboard(db: Session = Depends(get_db),
                      current_user=Depends(get_current_user)):
    student = _get_student(db, current_user.id)

    # Current enrollment
    enrollment = db.query(StudentCourse).filter_by(
        student_id=student.id, state="running").first()

    # Attendance summary
    present = db.query(AttendanceLine).filter_by(
        student_id=student.id, status=AttendanceStatus.PRESENT).count()
    absent = db.query(AttendanceLine).filter_by(
        student_id=student.id, status=AttendanceStatus.ABSENT).count()
    total_att = present + absent

    # Fee balance
    invoices = db.query(StudentFeeInvoice).filter_by(student_id=student.id).all()
    total_fees = sum(float(inv.total_amount or 0) for inv in invoices)
    total_paid = sum(float(inv.paid_amount or 0) for inv in invoices)

    # Pending assignments
    pending_subs = (db.query(Assignment)
                    .filter_by(active=True)
                    .filter(Assignment.course_id == (enrollment.course_id if enrollment else None))
                    .count()) if enrollment else 0

    return {
        "student_id": student.id,
        "name": f"{student.first_name} {student.last_name}",
        "admission_number": student.admission_number,
        "nemis_upi": student.nemis_upi,
        "class": enrollment.course.name if enrollment else None,
        "attendance": {
            "present": present, "absent": absent,
            "rate": round(present / total_att * 100, 1) if total_att > 0 else 0,
        },
        "fees": {
            "total": total_fees, "paid": total_paid,
            "balance": total_fees - total_paid,
        },
        "pending_assignments": pending_subs,
    }


# ── Timetable ─────────────────────────────────────────────────────────────────

@router.get("/timetable")
def my_timetable(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    student = _get_student(db, current_user.id)
    enrollment = db.query(StudentCourse).filter_by(
        student_id=student.id, state="running").first()
    if not enrollment:
        return []
    entries = (db.query(TimetableSlot)
               .filter_by(course_id=enrollment.course_id, is_active=True)
               .order_by(TimetableSlot.day_of_week, TimetableSlot.timing_id).all())
    return [
        {"day": e.day_of_week,
         "start_time": str(e.timing.start_time) if e.timing else None,
         "end_time": str(e.timing.end_time) if e.timing else None,
         "subject": e.subject.name if e.subject else None,
         "teacher": f"{e.teacher.first_name} {e.teacher.last_name}" if e.teacher else None,
         "room": e.classroom.name if e.classroom else None}
        for e in entries
    ]


# ── Attendance ────────────────────────────────────────────────────────────────

@router.get("/attendance")
def my_attendance(
    limit: int = 60,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    student = _get_student(db, current_user.id)
    lines = (db.query(AttendanceLine)
             .filter_by(student_id=student.id)
             .join(AttendanceSheet, AttendanceLine.sheet_id == AttendanceSheet.id)
             .order_by(AttendanceSheet.attendance_date.desc())
             .limit(limit).all())
    present = sum(1 for l in lines if l.status == AttendanceStatus.PRESENT)
    total = len(lines)
    return {
        "rate": round(present / total * 100, 1) if total > 0 else 0,
        "records": [
            {"date": l.sheet.attendance_date, "status": l.status, "note": l.note}
            for l in lines
        ]
    }


# ── Assignments ───────────────────────────────────────────────────────────────

@router.get("/assignments")
def my_assignments(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    student = _get_student(db, current_user.id)
    enrollment = db.query(StudentCourse).filter_by(
        student_id=student.id, state="running").first()
    if not enrollment:
        return []
    assignments = db.query(Assignment).filter_by(
        course_id=enrollment.course_id, active=True).all()
    result = []
    for a in assignments:
        sub = db.query(AssignmentSubmission).filter_by(
            assignment_id=a.id, student_id=student.id).first()
        result.append({
            "id": a.id, "name": a.name,
            "subject": a.subject.name if a.subject else None,
            "deadline": a.submission_date, "total_marks": a.total_marks,
            "submitted": sub is not None,
            "marks": sub.marks if sub else None,
            "state": sub.state if sub else None,
        })
    return result


# ── Exam Results ──────────────────────────────────────────────────────────────

@router.get("/results")
def my_results(
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    student = _get_student(db, current_user.id)
    q = db.query(ExamAttendees).filter_by(student_id=student.id)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {"total": total, "results": [
        {"exam_id": r.exam_id,
         "exam_name": r.exam.name if r.exam else None,
         "subject": r.exam.subject.name if r.exam and r.exam.subject else None,
         "marks": float(r.marks or 0), "state": r.state}
        for r in items
    ]}


# ── Fees ──────────────────────────────────────────────────────────────────────

@router.get("/fees")
def my_fees(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    student = _get_student(db, current_user.id)
    invoices = db.query(StudentFeeInvoice).filter_by(student_id=student.id).all()
    return {
        "summary": {
            "total": sum(float(i.total_amount or 0) for i in invoices),
            "paid": sum(float(i.paid_amount or 0) for i in invoices),
            "balance": sum(float((i.total_amount or 0) - (i.paid_amount or 0)) for i in invoices),
        },
        "invoices": [
            {"id": i.id, "total_amount": float(i.total_amount or 0),
             "paid_amount": float(i.paid_amount or 0),
             "balance": float((i.total_amount or 0) - (i.paid_amount or 0)),
             "due_date": i.due_date, "state": i.state}
            for i in invoices
        ]
    }


# ── Achievements & Activities ─────────────────────────────────────────────────

@router.get("/achievements")
def my_achievements(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    student = _get_student(db, current_user.id)
    items = db.query(Achievement).filter_by(student_id=student.id, active=True).all()
    return [{"id": a.id, "title": a.title, "date": a.date,
             "type": a.achievement_type.name if a.achievement_type else None,
             "certificate_number": a.certificate_number}
            for a in items]

@router.get("/activities")
def my_activities(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    student = _get_student(db, current_user.id)
    items = db.query(Activity).filter_by(student_id=student.id, active=True).all()
    return [{"id": a.id, "name": a.name, "date": a.date, "status": a.status,
             "type": a.activity_type.name if a.activity_type else None}
            for a in items]

@router.get("/scholarships")
def my_scholarships(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    student = _get_student(db, current_user.id)
    items = db.query(Scholarship).filter_by(student_id=student.id, active=True).all()
    return [{"id": s.id, "type": s.scholarship_type.name if s.scholarship_type else None,
             "amount": s.amount, "start_date": s.start_date,
             "end_date": s.end_date, "state": s.state}
            for s in items]
