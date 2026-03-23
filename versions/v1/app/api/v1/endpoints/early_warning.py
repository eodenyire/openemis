"""
AI Early Warning System — at-risk student flagging, dropout risk scoring,
teacher effectiveness, automated intervention alerts.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.people import Student, Teacher, StudentCourse
from app.models.core import AcademicYear
from app.models.attendance import AttendanceLine, AttendanceSheet, AttendanceRegister
from app.models.fees import StudentFeeInvoice
from app.models.cbc import ReportCard, ReportCardLine, PerformanceLevel

router = APIRouter()

# Weights for dropout risk score (sum = 100)
W_ATTENDANCE = 40
W_PERFORMANCE = 35
W_FEES = 25


def _attendance_rate(db: Session, student_id: int, year_id: int) -> float:
    total = (db.query(AttendanceLine)
             .join(AttendanceSheet, AttendanceSheet.id == AttendanceLine.sheet_id)
             .join(AttendanceRegister, AttendanceRegister.id == AttendanceSheet.register_id)
             .filter(AttendanceLine.student_id == student_id,
                     AttendanceRegister.academic_year_id == year_id).count())
    if not total:
        return 100.0
    present = (db.query(AttendanceLine)
               .join(AttendanceSheet, AttendanceSheet.id == AttendanceLine.sheet_id)
               .join(AttendanceRegister, AttendanceRegister.id == AttendanceSheet.register_id)
               .filter(AttendanceLine.student_id == student_id,
                       AttendanceRegister.academic_year_id == year_id,
                       AttendanceLine.status == "present").count())
    return round(present / total * 100, 1)


def _performance_score(db: Session, student_id: int, year_id: int) -> float:
    """Returns 0-100 based on EE/ME/AE/BE distribution."""
    level_weight = {"EE": 100, "ME": 75, "AE": 50, "BE": 25}
    lines = (db.query(ReportCardLine)
             .join(ReportCard, ReportCard.id == ReportCardLine.report_card_id)
             .filter(ReportCard.student_id == student_id,
                     ReportCard.academic_year_id == year_id).all())
    if not lines:
        return 75.0  # assume average if no data
    scores = [level_weight.get(str(l.performance_level), 50) for l in lines]
    return round(sum(scores) / len(scores), 1)


def _fee_arrears_rate(db: Session, student_id: int, year_id: int) -> float:
    """Returns 0-100 where 100 = fully paid, 0 = nothing paid."""
    inv = db.query(StudentFeeInvoice).filter_by(
        student_id=student_id, academic_year_id=year_id).first()
    if not inv or not inv.total_amount:
        return 100.0
    paid = float(inv.paid_amount or 0)
    total = float(inv.total_amount)
    return round(paid / total * 100, 1)


def _dropout_risk(att: float, perf: float, fees: float) -> dict:
    """
    Risk score 0-100 (higher = more at risk).
    Inverts each metric so low attendance/performance/payment = high risk.
    """
    risk = (
        (100 - att) * W_ATTENDANCE / 100 +
        (100 - perf) * W_PERFORMANCE / 100 +
        (100 - fees) * W_FEES / 100
    )
    risk = round(risk, 1)
    if risk >= 60:
        level = "HIGH"
    elif risk >= 35:
        level = "MEDIUM"
    else:
        level = "LOW"
    return {"score": risk, "level": level}


# ── At-risk students ──────────────────────────────────────────────────────────

@router.get("/at-risk")
def at_risk_students(
    academic_year_id: Optional[int] = None,
    risk_level: Optional[str] = Query(None, description="HIGH | MEDIUM | LOW"),
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Flag students with attendance < 75% OR 3+ consecutive BE grades."""
    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())
    if not year:
        return []

    students = db.query(Student).filter_by(active=True).all()
    flagged = []

    for student in students:
        att = _attendance_rate(db, student.id, year.id)
        perf = _performance_score(db, student.id, year.id)
        fees = _fee_arrears_rate(db, student.id, year.id)
        risk = _dropout_risk(att, perf, fees)

        # Flag triggers
        triggers = []
        if att < 75:
            triggers.append(f"Attendance {att}% (below 75%)")

        # Check consecutive BE grades
        lines = (db.query(ReportCardLine)
                 .join(ReportCard, ReportCard.id == ReportCardLine.report_card_id)
                 .filter(ReportCard.student_id == student.id,
                         ReportCard.academic_year_id == year.id)
                 .order_by(ReportCardLine.id.desc()).limit(5).all())
        be_streak = sum(1 for l in lines if str(l.performance_level) == "BE")
        if be_streak >= 3:
            triggers.append(f"{be_streak} consecutive BE grades")

        if float(fees) < 30:
            triggers.append(f"Fee payment only {fees}%")

        if not triggers and risk["level"] == "LOW":
            continue

        if risk_level and risk["level"] != risk_level:
            continue

        flagged.append({
            "student_id": student.id,
            "name": f"{student.first_name} {student.last_name}",
            "admission_number": student.admission_number,
            "attendance_rate": att,
            "performance_score": perf,
            "fee_payment_rate": fees,
            "risk_score": risk["score"],
            "risk_level": risk["level"],
            "triggers": triggers,
        })

    flagged.sort(key=lambda x: x["risk_score"], reverse=True)
    return flagged


@router.get("/dropout-risk/{student_id}")
def student_dropout_risk(
    student_id: int,
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Detailed dropout risk profile for a single student."""
    student = db.query(Student).get(student_id)
    if not student:
        from fastapi import HTTPException
        raise HTTPException(404, "Student not found")

    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())

    att = _attendance_rate(db, student_id, year.id if year else 0)
    perf = _performance_score(db, student_id, year.id if year else 0)
    fees = _fee_arrears_rate(db, student_id, year.id if year else 0)
    risk = _dropout_risk(att, perf, fees)

    return {
        "student_id": student_id,
        "name": f"{student.first_name} {student.last_name}",
        "factors": {
            "attendance_rate": att,
            "performance_score": perf,
            "fee_payment_rate": fees,
        },
        "weights": {
            "attendance": f"{W_ATTENDANCE}%",
            "performance": f"{W_PERFORMANCE}%",
            "fees": f"{W_FEES}%",
        },
        "risk_score": risk["score"],
        "risk_level": risk["level"],
        "recommendation": (
            "Immediate intervention required — contact parents and class teacher"
            if risk["level"] == "HIGH" else
            "Monitor closely — schedule counselling session"
            if risk["level"] == "MEDIUM" else
            "Student is on track"
        ),
    }


@router.get("/teacher-effectiveness")
def teacher_effectiveness(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Class average performance trend per teacher."""
    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())

    teachers = db.query(Teacher).filter_by(active=True).all()
    level_weight = {"EE": 4, "ME": 3, "AE": 2, "BE": 1}
    result = []

    for t in teachers:
        lines = (db.query(ReportCardLine)
                 .join(ReportCard, ReportCard.id == ReportCardLine.report_card_id)
                 .filter(ReportCard.class_teacher_id == t.id)
                 .all())
        if not lines:
            continue
        avg = sum(level_weight.get(str(l.performance_level), 0) for l in lines) / len(lines)
        result.append({
            "teacher_id": t.id,
            "name": f"{t.first_name} {t.last_name}",
            "students_assessed": len(lines),
            "avg_performance": round(avg, 2),
            "rating": "Excellent" if avg >= 3.5 else "Good" if avg >= 2.5 else "Needs Support",
        })

    result.sort(key=lambda x: x["avg_performance"], reverse=True)
    return result


@router.get("/summary")
def early_warning_summary(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Count of HIGH/MEDIUM/LOW risk students."""
    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())
    if not year:
        return {"high": 0, "medium": 0, "low": 0}

    # Quick count using attendance as primary signal
    students = db.query(Student).filter_by(active=True).all()
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for s in students:
        att = _attendance_rate(db, s.id, year.id)
        perf = _performance_score(db, s.id, year.id)
        fees = _fee_arrears_rate(db, s.id, year.id)
        level = _dropout_risk(att, perf, fees)["level"]
        counts[level] += 1

    return {
        "high_risk": counts["HIGH"],
        "medium_risk": counts["MEDIUM"],
        "low_risk": counts["LOW"],
        "total_students": len(students),
    }
