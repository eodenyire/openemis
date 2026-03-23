"""
Analytics endpoints — enrollment trends, attendance analytics,
CBC performance distribution, fee collection analytics, teacher workload.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.people import Student, Teacher, StudentCourse
from app.models.core import AcademicYear, AcademicTerm, Course, Batch
from app.models.attendance import AttendanceLine, AttendanceSheet, AttendanceRegister
from app.models.fees import FeePayment, StudentFeeInvoice
from app.models.cbc import CompetencyScore, PerformanceLevel, ReportCard, ReportCardLine
from app.models.hr import StaffProfile

router = APIRouter()


# ── Enrollment analytics ──────────────────────────────────────────────────────

@router.get("/enrollment/trends")
def enrollment_trends(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Enrollment count per academic year."""
    years = db.query(AcademicYear).order_by(AcademicYear.id).all()
    result = []
    for year in years:
        count = db.query(StudentCourse).filter_by(
            academic_year_id=year.id, active=True).count()
        result.append({"year": year.name, "enrolled": count})
    return result


@router.get("/enrollment/by-grade")
def enrollment_by_grade(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Enrollment breakdown per course/grade."""
    q = db.query(Course.name, func.count(StudentCourse.id).label("count"))\
        .join(StudentCourse, StudentCourse.course_id == Course.id)\
        .filter(StudentCourse.active == True)
    if academic_year_id:
        q = q.filter(StudentCourse.academic_year_id == academic_year_id)
    rows = q.group_by(Course.name).order_by(Course.name).all()
    return [{"grade": r.name, "enrolled": r.count} for r in rows]


@router.get("/enrollment/by-gender")
def enrollment_by_gender(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    from app.models.core import Gender
    q = db.query(Student.gender, func.count(Student.id).label("count"))\
        .join(StudentCourse, StudentCourse.student_id == Student.id)\
        .filter(StudentCourse.active == True)
    if academic_year_id:
        q = q.filter(StudentCourse.academic_year_id == academic_year_id)
    rows = q.group_by(Student.gender).all()
    return [{"gender": str(r.gender), "count": r.count} for r in rows]


# ── Attendance analytics ──────────────────────────────────────────────────────

@router.get("/attendance/summary")
def attendance_summary(
    academic_year_id: Optional[int] = None,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """School-wide attendance rate."""
    q = db.query(
        func.count(AttendanceLine.id).label("total"),
        func.sum(case((AttendanceLine.status == "present", 1), else_=0)).label("present"),
        func.sum(case((AttendanceLine.status == "absent", 1), else_=0)).label("absent"),
        func.sum(case((AttendanceLine.status == "late", 1), else_=0)).label("late"),
    ).join(AttendanceSheet, AttendanceSheet.id == AttendanceLine.sheet_id)\
     .join(AttendanceRegister, AttendanceRegister.id == AttendanceSheet.register_id)
    if academic_year_id:
        q = q.filter(AttendanceRegister.academic_year_id == academic_year_id)
    if course_id:
        q = q.filter(AttendanceRegister.course_id == course_id)
    row = q.first()
    total = row.total or 1
    return {
        "total_records": row.total or 0,
        "present": row.present or 0,
        "absent": row.absent or 0,
        "late": row.late or 0,
        "attendance_rate": round((row.present or 0) / total * 100, 1),
    }


@router.get("/attendance/low-attenders")
def low_attenders(
    threshold: float = Query(75.0, description="Attendance % threshold"),
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Students below the attendance threshold."""
    q = db.query(
        Student.id, Student.first_name, Student.last_name, Student.admission_number,
        func.count(AttendanceLine.id).label("total"),
        func.sum(case((AttendanceLine.status == "present", 1), else_=0)).label("present"),
    ).join(AttendanceLine, AttendanceLine.student_id == Student.id)\
     .join(AttendanceSheet, AttendanceSheet.id == AttendanceLine.sheet_id)\
     .join(AttendanceRegister, AttendanceRegister.id == AttendanceSheet.register_id)
    if academic_year_id:
        q = q.filter(AttendanceRegister.academic_year_id == academic_year_id)
    rows = q.group_by(Student.id, Student.first_name, Student.last_name,
                      Student.admission_number).all()
    at_risk = []
    for r in rows:
        rate = round((r.present or 0) / (r.total or 1) * 100, 1)
        if rate < threshold:
            at_risk.append({
                "student_id": r.id,
                "name": f"{r.first_name} {r.last_name}",
                "admission_number": r.admission_number,
                "attendance_rate": rate,
                "days_present": r.present or 0,
                "days_total": r.total or 0,
            })
    at_risk.sort(key=lambda x: x["attendance_rate"])
    return at_risk


# ── CBC performance analytics ─────────────────────────────────────────────────

@router.get("/performance/distribution")
def performance_distribution(
    academic_year_id: Optional[int] = None,
    grade_level_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """EE/ME/AE/BE distribution across all report card lines."""
    q = db.query(
        ReportCardLine.performance_level,
        func.count(ReportCardLine.id).label("count")
    ).join(ReportCard, ReportCard.id == ReportCardLine.report_card_id)
    if academic_year_id:
        q = q.filter(ReportCard.academic_year_id == academic_year_id)
    if grade_level_id:
        q = q.filter(ReportCard.grade_level_id == grade_level_id)
    rows = q.group_by(ReportCardLine.performance_level).all()
    total = sum(r.count for r in rows) or 1
    return {
        str(r.performance_level): {
            "count": r.count,
            "percentage": round(r.count / total * 100, 1),
        }
        for r in rows
    }


@router.get("/performance/by-grade")
def performance_by_grade(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Average performance level per grade."""
    from app.models.cbc import CBCGradeLevel
    grades = db.query(CBCGradeLevel).filter_by(is_active=True).order_by(CBCGradeLevel.order).all()
    result = []
    level_weight = {"EE": 4, "ME": 3, "AE": 2, "BE": 1}
    for grade in grades:
        q = db.query(ReportCardLine.performance_level, func.count(ReportCardLine.id))\
            .join(ReportCard, ReportCard.id == ReportCardLine.report_card_id)\
            .filter(ReportCard.grade_level_id == grade.id)
        if academic_year_id:
            q = q.filter(ReportCard.academic_year_id == academic_year_id)
        rows = q.group_by(ReportCardLine.performance_level).all()
        dist = {str(pl): cnt for pl, cnt in rows}
        total = sum(dist.values()) or 1
        weighted = sum(level_weight.get(str(pl), 0) * cnt for pl, cnt in rows)
        result.append({
            "grade": grade.name,
            "distribution": dist,
            "avg_score": round(weighted / total, 2),
        })
    return result


# ── Fee collection analytics ──────────────────────────────────────────────────

@router.get("/fees/collection")
def fee_collection(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Collected vs outstanding fees."""
    q_inv = db.query(func.sum(StudentFeeInvoice.total_amount).label("invoiced"),
                     func.sum(StudentFeeInvoice.paid_amount).label("paid"))
    if academic_year_id:
        q_inv = q_inv.filter(StudentFeeInvoice.academic_year_id == academic_year_id)
    row = q_inv.first()
    invoiced = float(row.invoiced or 0)
    paid = float(row.paid or 0)
    return {
        "total_invoiced": invoiced,
        "total_collected": paid,
        "outstanding": round(invoiced - paid, 2),
        "collection_rate": round(paid / invoiced * 100, 1) if invoiced else 0,
    }


@router.get("/fees/payment-methods")
def payment_methods(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Breakdown of payments by method (M-Pesa, cash, bank)."""
    q = db.query(FeePayment.payment_method,
                 func.count(FeePayment.id).label("count"),
                 func.sum(FeePayment.amount).label("total"))
    if academic_year_id:
        q = q.join(StudentFeeInvoice, StudentFeeInvoice.id == FeePayment.invoice_id)\
             .filter(StudentFeeInvoice.academic_year_id == academic_year_id)
    rows = q.group_by(FeePayment.payment_method).all()
    return [{"method": str(r.payment_method), "count": r.count,
             "total": float(r.total or 0)} for r in rows]


# ── Teacher workload analytics ────────────────────────────────────────────────

@router.get("/teachers/workload")
def teacher_workload(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Number of subjects and students per teacher."""
    from app.models.core import teacher_subjects
    from sqlalchemy import select
    teachers = db.query(Teacher).filter_by(active=True).all()
    result = []
    for t in teachers:
        subject_count = len(t.subjects)
        result.append({
            "teacher_id": t.id,
            "name": f"{t.first_name} {t.last_name}",
            "subjects": subject_count,
        })
    result.sort(key=lambda x: x["subjects"], reverse=True)
    return result


@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Top-level numbers for the analytics dashboard."""
    total_students = db.query(Student).filter_by(active=True).count()
    total_teachers = db.query(Teacher).filter_by(active=True).count()
    year = db.query(AcademicYear).order_by(AcademicYear.id.desc()).first()
    enrolled = db.query(StudentCourse).filter_by(
        academic_year_id=year.id if year else None, active=True).count() if year else 0
    total_att = db.query(AttendanceLine).count()
    present = db.query(AttendanceLine).filter(AttendanceLine.status == "present").count()
    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "current_enrollment": enrolled,
        "overall_attendance_rate": round(present / total_att * 100, 1) if total_att else 0,
        "report_cards_issued": db.query(ReportCard).filter_by(is_published=True).count(),
    }
