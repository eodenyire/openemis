"""Student lifecycle endpoints — promotions, transfers, alumni."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.db.session import get_db
from app.api.deps import require_admin, get_current_user
from app.models.people import Student, StudentCourse
from app.models.core import AcademicYear, AcademicTerm

router = APIRouter()


class PromotionRequest(BaseModel):
    from_academic_year_id: int
    to_academic_year_id: int
    to_academic_term_id: int
    course_ids: Optional[list[int]] = None  # if None, promote all


@router.post("/promote")
def bulk_promote(
    payload: PromotionRequest,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Promote all students from one academic year to the next."""
    query = db.query(StudentCourse).filter(
        StudentCourse.academic_year_id == payload.from_academic_year_id,
        StudentCourse.state == "running",
    )
    if payload.course_ids:
        query = query.filter(StudentCourse.course_id.in_(payload.course_ids))

    enrollments = query.all()
    promoted = 0
    for sc in enrollments:
        sc.state = "finished"
        new_sc = StudentCourse(
            student_id=sc.student_id,
            course_id=sc.course_id,
            batch_id=sc.batch_id,
            academic_year_id=payload.to_academic_year_id,
            academic_term_id=payload.to_academic_term_id,
            state="running",
            fees_start_date=date.today(),
        )
        db.add(new_sc)
        promoted += 1

    db.commit()
    return {"promoted": promoted, "message": f"Promoted {promoted} students"}


class TransferRequest(BaseModel):
    student_id: int
    to_course_id: int
    to_batch_id: int
    academic_year_id: int
    academic_term_id: int
    reason: Optional[str] = None


@router.post("/transfer")
def transfer_student(
    payload: TransferRequest,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    student = db.query(Student).filter(Student.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Close current enrollment
    current = db.query(StudentCourse).filter(
        StudentCourse.student_id == payload.student_id,
        StudentCourse.state == "running",
    ).first()
    if current:
        current.state = "transferred"

    new_sc = StudentCourse(
        student_id=payload.student_id,
        course_id=payload.to_course_id,
        batch_id=payload.to_batch_id,
        academic_year_id=payload.academic_year_id,
        academic_term_id=payload.academic_term_id,
        state="running",
        fees_start_date=date.today(),
    )
    db.add(new_sc)
    db.commit()
    return {"message": "Student transferred successfully", "student_id": payload.student_id}


@router.get("/student/{student_id}/history")
def student_history(
    student_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    enrollments = db.query(StudentCourse).filter(
        StudentCourse.student_id == student_id
    ).all()
    return enrollments
