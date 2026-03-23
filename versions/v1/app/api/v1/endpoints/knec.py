"""
KNEC Integration — exam registration export, exam centre management,
results import, candidate result slips.
"""
import csv
import io
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.people import Student, StudentCourse
from app.models.core import AcademicYear, Course
from app.models.exam import ExamAttendees, Exam

router = APIRouter()

# KNEC exam types
KJSEA = "KJSEA"   # Grade 9 — Kenya Junior Secondary Education Assessment
KCSE  = "KCSE"    # Grade 12 — Kenya Certificate of Secondary Education


class ExamCentre(BaseModel):
    code: str
    name: str
    county: str
    capacity: int


# In-memory exam centres store (replace with DB model if needed)
_exam_centres: List[dict] = []


# ── Candidate list export ─────────────────────────────────────────────────────

@router.get("/export/candidates")
def export_candidates(
    exam_type: str = Query(..., description="KJSEA or KCSE"),
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Export KNEC candidate registration list as CSV."""
    if exam_type not in (KJSEA, KCSE):
        raise HTTPException(400, f"exam_type must be {KJSEA} or {KCSE}")

    # Grade 9 for KJSEA, Grade 12 for KCSE
    target_grade = "Grade 9" if exam_type == KJSEA else "Grade 12"

    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())

    q = db.query(Student, Course.name.label("grade"))\
        .join(StudentCourse, StudentCourse.student_id == Student.id)\
        .join(Course, Course.id == StudentCourse.course_id)\
        .filter(StudentCourse.active == True, Student.active == True,
                Course.name == target_grade)
    if year:
        q = q.filter(StudentCourse.academic_year_id == year.id)

    rows = q.all()
    if not rows:
        raise HTTPException(404, f"No {target_grade} students found for {exam_type}")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Index_Number", "NEMIS_UPI", "Surname", "Other_Names",
        "Gender", "Date_of_Birth", "Nationality", "Exam_Type", "Year",
    ])
    for i, (student, grade) in enumerate(rows, 1):
        index = f"{exam_type[:3]}/{year.name if year else '2026'}/{i:04d}"
        writer.writerow([
            index,
            student.nemis_upi or "",
            student.last_name,
            f"{student.first_name} {student.middle_name or ''}".strip(),
            str(student.gender) if student.gender else "",
            str(student.date_of_birth) if student.date_of_birth else "",
            student.nationality or "Kenyan",
            exam_type,
            year.name if year else "",
        ])

    output.seek(0)
    filename = f"knec_{exam_type.lower()}_candidates_{year.name if year else 'export'}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ── Exam centres ──────────────────────────────────────────────────────────────

@router.get("/centres")
def list_centres(_=Depends(get_current_user)):
    return _exam_centres


@router.post("/centres", status_code=201)
def add_centre(data: ExamCentre, _=Depends(require_admin)):
    if any(c["code"] == data.code for c in _exam_centres):
        raise HTTPException(409, "Centre code already exists")
    centre = data.model_dump()
    _exam_centres.append(centre)
    return centre


@router.delete("/centres/{code}", status_code=204)
def remove_centre(code: str, _=Depends(require_admin)):
    global _exam_centres
    _exam_centres = [c for c in _exam_centres if c["code"] != code]


# ── Results import ────────────────────────────────────────────────────────────

@router.post("/results/import")
async def import_results(
    file: UploadFile = File(...),
    exam_type: str = Query(..., description="KJSEA or KCSE"),
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(require_admin)
):
    """
    Import KNEC results from CSV.
    Expected columns: NEMIS_UPI, Subject, Grade, Points
    """
    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())

    imported, skipped, errors = 0, 0, []

    for row in reader:
        upi = row.get("NEMIS_UPI", "").strip()
        subject = row.get("Subject", "").strip()
        grade = row.get("Grade", "").strip()
        points = row.get("Points", "0").strip()

        if not upi or not subject:
            skipped += 1
            continue

        student = db.query(Student).filter_by(nemis_upi=upi).first()
        if not student:
            errors.append({"upi": upi, "error": "Student not found"})
            continue

        # Find or create a KNEC exam session exam to attach results to
        try:
            # Look for an existing KNEC exam for this subject
            exam = db.query(Exam).filter(Exam.name.ilike(f"%{exam_type}%")).first()
            if not exam:
                skipped += 1
                errors.append({"upi": upi, "error": f"No {exam_type} exam found — create exam first"})
                continue
            attendee = ExamAttendees(
                exam_id=exam.id,
                student_id=student.id,
                marks=float(points) if points else 0,
                state="pass" if grade in ("A", "B", "C") else "fail",
            )
            db.add(attendee)
            imported += 1
        except Exception as e:
            errors.append({"upi": upi, "error": str(e)})

    db.commit()
    return {
        "imported": imported,
        "skipped": skipped,
        "errors": len(errors),
        "error_details": errors[:20],  # cap at 20
    }


# ── Candidate result slips ────────────────────────────────────────────────────

@router.get("/results/slip/{student_id}")
def result_slip(
    student_id: int,
    exam_type: str = Query(..., description="KJSEA or KCSE"),
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """Return structured result slip data for a candidate."""
    student = db.query(Student).get(student_id)
    if not student:
        raise HTTPException(404, "Student not found")

    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())

    results = db.query(ExamAttendees)\
        .join(Exam, Exam.id == ExamAttendees.exam_id)\
        .filter(ExamAttendees.student_id == student_id,
                Exam.name.ilike(f"%{exam_type}%")).all()

    return {
        "exam_type": exam_type,
        "year": year.name if year else None,
        "candidate": {
            "name": f"{student.first_name} {student.last_name}",
            "nemis_upi": student.nemis_upi,
            "admission_number": student.admission_number,
            "gender": str(student.gender) if student.gender else None,
        },
        "results": [
            {"subject": r.exam.subject.name if r.exam and r.exam.subject else "N/A",
             "marks": r.marks, "state": r.state}
            for r in results
        ],
        "total_marks": sum(r.marks or 0 for r in results),
    }


@router.get("/summary")
def knec_summary(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    """KNEC readiness summary."""
    year = (db.query(AcademicYear).filter_by(id=academic_year_id).first()
            if academic_year_id
            else db.query(AcademicYear).order_by(AcademicYear.id.desc()).first())

    def count_grade(grade_name):
        q = db.query(Student)\
            .join(StudentCourse, StudentCourse.student_id == Student.id)\
            .join(Course, Course.id == StudentCourse.course_id)\
            .filter(StudentCourse.active == True, Student.active == True,
                    Course.name == grade_name)
        if year:
            q = q.filter(StudentCourse.academic_year_id == year.id)
        return q.count()

    g9 = count_grade("Grade 9")
    g12 = count_grade("Grade 12")

    return {
        "academic_year": year.name if year else None,
        "kjsea_candidates": g9,
        "kcse_candidates": g12,
        "exam_centres": len(_exam_centres),
    }
