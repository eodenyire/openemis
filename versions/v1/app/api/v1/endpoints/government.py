"""
Government Dashboard — read-only analytics for Ministry of Education users.
County-level stats, school performance, CBC compliance, teacher-student ratios,
infrastructure reports.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.people import Student, Teacher, StudentCourse
from app.models.core import AcademicYear, Course
from app.models.cbc import ReportCard, ReportCardLine, CBCGradeLevel
from app.models.attendance import AttendanceLine
from app.models.fees import StudentFeeInvoice

router = APIRouter()


# ── County-level enrollment ───────────────────────────────────────────────────

@router.get("/enrollment/by-county")
def enrollment_by_county(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Enrollment grouped by student county/state field."""
    q = db.query(Student.state.label("county"), func.count(Student.id).label("count"))\
        .join(StudentCourse, StudentCourse.student_id == Student.id)\
        .filter(StudentCourse.active == True, Student.active == True)
    if academic_year_id:
        q = q.filter(StudentCourse.academic_year_id == academic_year_id)
    rows = q.group_by(Student.state).order_by(func.count(Student.id).desc()).all()
    return [{"county": r.county or "Unknown", "enrolled": r.count} for r in rows]


@router.get("/enrollment/summary")
def enrollment_summary(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Top-level enrollment numbers."""
    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())

    total_students = db.query(Student).filter_by(active=True).count()
    total_teachers = db.query(Teacher).filter_by(active=True).count()
    enrolled = 0
    if year:
        enrolled = db.query(StudentCourse).filter_by(
            academic_year_id=year.id, active=True).count()

    ratio = round(total_students / total_teachers, 1) if total_teachers else 0

    return {
        "academic_year": year.name if year else None,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "current_enrollment": enrolled,
        "teacher_student_ratio": f"1:{ratio}",
    }


# ── Performance league table ──────────────────────────────────────────────────

@router.get("/performance/league-table")
def performance_league_table(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """
    Grade-level performance ranking (anonymized — no student names).
    Shows EE/ME/AE/BE distribution per grade.
    """
    grades = db.query(CBCGradeLevel).filter_by(is_active=True)\
        .order_by(CBCGradeLevel.order).all()
    level_weight = {"EE": 4, "ME": 3, "AE": 2, "BE": 1}
    result = []

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
        avg = round(weighted / total, 2)

        result.append({
            "grade": grade.name,
            "band": str(grade.grade_band),
            "avg_score": avg,
            "distribution": dist,
            "students_assessed": total,
        })

    result.sort(key=lambda x: x["avg_score"], reverse=True)
    return result


# ── CBC compliance ────────────────────────────────────────────────────────────

@router.get("/cbc-compliance")
def cbc_compliance(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """CBC compliance metrics: report cards issued, assessments done."""
    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())

    total_students = db.query(Student).filter_by(active=True).count()

    q_rc = db.query(ReportCard)
    if year:
        q_rc = q_rc.filter_by(academic_year_id=year.id)
    total_report_cards = q_rc.count()
    published = q_rc.filter_by(is_published=True).count() if year else 0

    from app.models.cbc import CBCAssessment
    total_assessments = db.query(CBCAssessment).count()

    return {
        "academic_year": year.name if year else None,
        "total_students": total_students,
        "report_cards_generated": total_report_cards,
        "report_cards_published": published,
        "report_card_coverage": round(total_report_cards / total_students * 100, 1) if total_students else 0,
        "total_assessments_conducted": total_assessments,
        "cbc_grade_levels_active": db.query(CBCGradeLevel).filter_by(is_active=True).count(),
    }


# ── Teacher-student ratio ─────────────────────────────────────────────────────

@router.get("/ratios")
def ratios(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Teacher-student ratio per grade."""
    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())

    courses = db.query(Course).filter_by(active=True).all()
    result = []
    for course in courses:
        q = db.query(func.count(StudentCourse.id))\
            .filter_by(course_id=course.id, active=True)
        if year:
            q = q.filter_by(academic_year_id=year.id)
        student_count = q.scalar() or 0

        # Teachers linked via batches/subjects — approximate via subject teachers
        teacher_count = len(set(
            t.id for s in course.subjects for t in s.teachers
        )) if hasattr(course, "subjects") else 0

        result.append({
            "grade": course.name,
            "students": student_count,
            "teachers": teacher_count,
            "ratio": f"1:{round(student_count / teacher_count, 1)}" if teacher_count else "N/A",
        })

    return result


# ── Infrastructure report ─────────────────────────────────────────────────────

@router.get("/infrastructure")
def infrastructure_report(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Basic infrastructure counts."""
    from app.models.hostel import HostelRoom, HostelBlock
    from app.models.library import Media
    from app.models.transportation import Vehicle, TransportRoute

    return {
        "hostel_blocks": db.query(HostelBlock).count(),
        "hostel_rooms": db.query(HostelRoom).filter_by(active=True).count(),
        "library_titles": db.query(Media).filter_by(active=True).count(),
        "transport_vehicles": db.query(Vehicle).filter_by(active=True).count(),
        "transport_routes": db.query(TransportRoute).filter_by(active=True).count(),
        "total_teachers": db.query(Teacher).filter_by(active=True).count(),
        "total_students": db.query(Student).filter_by(active=True).count(),
    }


# ── Master government summary ─────────────────────────────────────────────────

@router.get("/summary")
def government_summary(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Single endpoint for the government dashboard overview."""
    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())

    total_students = db.query(Student).filter_by(active=True).count()
    total_teachers = db.query(Teacher).filter_by(active=True).count()
    enrolled = db.query(StudentCourse).filter_by(
        academic_year_id=year.id, active=True).count() if year else 0

    # Attendance rate
    total_att = db.query(AttendanceLine).count()
    present = db.query(AttendanceLine).filter(AttendanceLine.status == "present").count()
    att_rate = round(present / total_att * 100, 1) if total_att else 0

    # NEMIS coverage
    with_upi = db.query(Student).filter(
        Student.active == True,
        Student.nemis_upi != None,
        Student.nemis_upi != "").count()

    return {
        "academic_year": year.name if year else None,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "current_enrollment": enrolled,
        "teacher_student_ratio": f"1:{round(total_students / total_teachers, 1)}" if total_teachers else "N/A",
        "attendance_rate": att_rate,
        "nemis_upi_coverage": round(with_upi / total_students * 100, 1) if total_students else 0,
        "report_cards_published": db.query(ReportCard).filter_by(is_published=True).count(),
    }
