"""
NEMIS Integration — UPI sync, bulk enrollment export, MoE statistics,
UPI validation flagging.
"""
import csv
import io
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.people import Student, StudentCourse
from app.models.core import AcademicYear, Course, Gender

router = APIRouter()


class UPIUpdate(BaseModel):
    student_id: int
    nemis_upi: str


class BulkUPIUpdate(BaseModel):
    updates: List[UPIUpdate]


# ── UPI management ────────────────────────────────────────────────────────────

@router.get("/students/missing-upi")
def students_missing_upi(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """List active students without a NEMIS UPI."""
    students = (db.query(Student)
                .filter(Student.active == True)
                .filter((Student.nemis_upi == None) | (Student.nemis_upi == ""))
                .offset(skip).limit(limit).all())
    return [
        {"student_id": s.id, "name": f"{s.first_name} {s.last_name}",
         "admission_number": s.admission_number, "nemis_upi": s.nemis_upi}
        for s in students
    ]


@router.put("/students/upi")
def update_upi(data: UPIUpdate, db: Session = Depends(get_db),
               _=Depends(require_admin)):
    """Update NEMIS UPI for a single student."""
    student = db.query(Student).get(data.student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    # Check uniqueness
    existing = db.query(Student).filter(
        Student.nemis_upi == data.nemis_upi,
        Student.id != data.student_id).first()
    if existing:
        raise HTTPException(409, f"UPI {data.nemis_upi} already assigned to another student")
    student.nemis_upi = data.nemis_upi
    db.commit()
    return {"student_id": student.id, "nemis_upi": student.nemis_upi}


@router.put("/students/upi/bulk")
def bulk_update_upi(data: BulkUPIUpdate, db: Session = Depends(get_db),
                    _=Depends(require_admin)):
    """Bulk update NEMIS UPIs."""
    updated, errors = [], []
    for item in data.updates:
        student = db.query(Student).get(item.student_id)
        if not student:
            errors.append({"student_id": item.student_id, "error": "Not found"})
            continue
        student.nemis_upi = item.nemis_upi
        updated.append(item.student_id)
    db.commit()
    return {"updated": len(updated), "errors": errors}


# ── Bulk enrollment export ────────────────────────────────────────────────────

@router.get("/export/enrollment")
def export_enrollment_csv(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Export NEMIS-compatible enrollment CSV."""
    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())

    q = db.query(Student, Course.name.label("grade"))\
        .join(StudentCourse, StudentCourse.student_id == Student.id)\
        .join(Course, Course.id == StudentCourse.course_id)\
        .filter(StudentCourse.active == True, Student.active == True)
    if year:
        q = q.filter(StudentCourse.academic_year_id == year.id)

    rows = q.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "NEMIS_UPI", "Admission_Number", "First_Name", "Middle_Name", "Last_Name",
        "Gender", "Date_of_Birth", "Grade", "Nationality", "County",
    ])
    for student, grade in rows:
        writer.writerow([
            student.nemis_upi or "",
            student.admission_number,
            student.first_name,
            student.middle_name or "",
            student.last_name,
            str(student.gender) if student.gender else "",
            str(student.date_of_birth) if student.date_of_birth else "",
            grade,
            student.nationality or "Kenyan",
            student.state or "",
        ])

    output.seek(0)
    filename = f"nemis_enrollment_{year.name if year else 'export'}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ── MoE statistics report ─────────────────────────────────────────────────────

@router.get("/statistics")
def moe_statistics(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """School statistics in MoE format: enrollment by gender, grade, special needs."""
    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())

    total = db.query(Student).filter_by(active=True).count()
    missing_upi = db.query(Student).filter(
        Student.active == True,
        (Student.nemis_upi == None) | (Student.nemis_upi == "")).count()

    # Gender breakdown
    from sqlalchemy import func
    gender_rows = db.query(Student.gender, func.count(Student.id))\
        .filter_by(active=True).group_by(Student.gender).all()
    gender_dist = {str(g): c for g, c in gender_rows}

    # Grade breakdown
    grade_rows = db.query(Course.name, func.count(StudentCourse.id))\
        .join(StudentCourse, StudentCourse.course_id == Course.id)\
        .filter(StudentCourse.active == True)
    if year:
        grade_rows = grade_rows.filter(StudentCourse.academic_year_id == year.id)
    grade_rows = grade_rows.group_by(Course.name).order_by(Course.name).all()

    return {
        "academic_year": year.name if year else None,
        "total_enrolled": total,
        "students_with_upi": total - missing_upi,
        "students_missing_upi": missing_upi,
        "upi_coverage": round((total - missing_upi) / total * 100, 1) if total else 0,
        "gender_distribution": gender_dist,
        "enrollment_by_grade": {name: count for name, count in grade_rows},
    }


@router.get("/validation")
def validate_upi_data(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Flag data quality issues: missing UPI, duplicate UPI, missing DOB."""
    from sqlalchemy import func
    issues = []

    # Missing UPI
    missing = db.query(Student).filter(
        Student.active == True,
        (Student.nemis_upi == None) | (Student.nemis_upi == "")).count()
    if missing:
        issues.append({"type": "missing_upi", "count": missing,
                       "severity": "HIGH", "action": "Assign NEMIS UPI via /nemis/students/upi"})

    # Duplicate UPIs
    dupes = (db.query(Student.nemis_upi, func.count(Student.id).label("cnt"))
             .filter(Student.nemis_upi != None, Student.nemis_upi != "")
             .group_by(Student.nemis_upi)
             .having(func.count(Student.id) > 1).all())
    if dupes:
        issues.append({"type": "duplicate_upi", "count": len(dupes),
                       "severity": "HIGH",
                       "duplicates": [{"upi": d.nemis_upi, "count": d.cnt} for d in dupes]})

    # Missing DOB
    no_dob = db.query(Student).filter(
        Student.active == True, Student.date_of_birth == None).count()
    if no_dob:
        issues.append({"type": "missing_dob", "count": no_dob, "severity": "MEDIUM"})

    return {"total_issues": len(issues), "issues": issues}
