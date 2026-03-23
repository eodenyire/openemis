"""CBC Curriculum API — Grade Levels, Learning Areas, Strands, Report Cards."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db.session import get_db
from app.api.deps import get_current_user, require_permission
from app.models.cbc import (
    CBCGradeLevel, LearningArea, Strand, SubStrand,
    CompetencyIndicator, ReportCard, ReportCardLine,
    CompetencyScore, CBCAssessment, PerformanceLevel,
)
from app.core.cbc_utils import score_to_cbc_level

router = APIRouter()


# ── Grade Levels ──────────────────────────────────────────────────────────────

@router.get("/grade-levels")
def list_grade_levels(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(CBCGradeLevel).order_by(CBCGradeLevel.order).all()


@router.get("/grade-levels/{grade_id}/learning-areas")
def get_learning_areas(grade_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(LearningArea).filter(LearningArea.grade_level_id == grade_id).all()


# ── Strands ───────────────────────────────────────────────────────────────────

@router.get("/learning-areas/{la_id}/strands")
def get_strands(la_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Strand).filter(Strand.learning_area_id == la_id).order_by(Strand.order).all()


@router.get("/strands/{strand_id}/sub-strands")
def get_sub_strands(strand_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(SubStrand).filter(SubStrand.strand_id == strand_id).order_by(SubStrand.order).all()


# ── Report Cards ──────────────────────────────────────────────────────────────

@router.get("/report-cards/student/{student_id}")
def get_student_report_cards(
    student_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return db.query(ReportCard).filter(ReportCard.student_id == student_id).all()


class ReportCardCreate(BaseModel):
    student_id: int
    grade_level_id: int
    academic_year_id: int
    academic_term_id: int
    teacher_remarks: str = ""
    days_present: int = 0
    days_absent: int = 0


@router.post("/report-cards")
def create_report_card(
    payload: ReportCardCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("reports:write:class")),
):
    rc = ReportCard(**payload.model_dump())
    db.add(rc)
    db.commit()
    db.refresh(rc)
    return rc


# ── Score Utility ─────────────────────────────────────────────────────────────

@router.get("/score-to-level")
def convert_score(score: float, _=Depends(get_current_user)):
    level = score_to_cbc_level(score)
    return {"score": score, "performance_level": level.value}
