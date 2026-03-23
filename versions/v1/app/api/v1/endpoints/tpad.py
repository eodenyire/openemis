"""TPAD appraisal endpoints — Kenya TSC Teacher Performance Appraisal & Development."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.hr import TPADAppraisal, TPADRating, StaffProfile

router = APIRouter()

SCORE_WEIGHTS = {
    "professional_knowledge": 1,
    "lesson_planning": 1,
    "classroom_management": 1,
    "teaching_methodology": 1,
    "student_assessment": 1,
    "professional_development": 1,
    "co_curricular": 1,
    "community_engagement": 1,
}
COMPETENCY_FIELDS = list(SCORE_WEIGHTS.keys())


def _compute_rating(avg: float) -> TPADRating:
    if avg >= 4.5: return TPADRating.OUTSTANDING
    if avg >= 3.5: return TPADRating.EXCEEDS
    if avg >= 2.5: return TPADRating.MEETS
    if avg >= 1.5: return TPADRating.BELOW
    return TPADRating.UNSATISFACTORY


# ── Schemas ───────────────────────────────────────────────────────────────────

class TPADCreate(BaseModel):
    staff_id: int
    appraiser_id: int
    academic_year_id: int
    appraisal_period: str  # "mid_year" | "end_year"
    professional_knowledge: float = 0
    lesson_planning: float = 0
    classroom_management: float = 0
    teaching_methodology: float = 0
    student_assessment: float = 0
    professional_development: float = 0
    co_curricular: float = 0
    community_engagement: float = 0
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    targets_next_period: Optional[str] = None
    appraiser_comments: Optional[str] = None

    @validator('professional_knowledge', 'lesson_planning', 'classroom_management',
               'teaching_methodology', 'student_assessment', 'professional_development',
               'co_curricular', 'community_engagement', pre=True, always=True)
    def score_range(cls, v):
        if not (0 <= float(v) <= 5):
            raise ValueError("Scores must be between 0 and 5")
        return v

    @validator('appraisal_period')
    def valid_period(cls, v):
        if v not in ("mid_year", "end_year"):
            raise ValueError("appraisal_period must be 'mid_year' or 'end_year'")
        return v

class TPADUpdate(BaseModel):
    professional_knowledge: Optional[float] = None
    lesson_planning: Optional[float] = None
    classroom_management: Optional[float] = None
    teaching_methodology: Optional[float] = None
    student_assessment: Optional[float] = None
    professional_development: Optional[float] = None
    co_curricular: Optional[float] = None
    community_engagement: Optional[float] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    targets_next_period: Optional[str] = None
    appraiser_comments: Optional[str] = None
    staff_comments: Optional[str] = None

class TPADOut(BaseModel):
    id: int
    staff_id: int
    appraiser_id: int
    academic_year_id: int
    appraisal_period: str
    professional_knowledge: float
    lesson_planning: float
    classroom_management: float
    teaching_methodology: float
    student_assessment: float
    professional_development: float
    co_curricular: float
    community_engagement: float
    total_score: float
    average_score: float
    rating: Optional[str]
    strengths: Optional[str]
    areas_for_improvement: Optional[str]
    targets_next_period: Optional[str]
    is_submitted: bool
    is_acknowledged: bool
    class Config: from_attributes = True


def _recalculate(appraisal: TPADAppraisal):
    scores = [getattr(appraisal, f) or 0 for f in COMPETENCY_FIELDS]
    appraisal.total_score = round(sum(scores), 2)
    appraisal.average_score = round(sum(scores) / len(scores), 2)
    appraisal.rating = _compute_rating(appraisal.average_score)


# ── TPAD CRUD ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[TPADOut])
def list_appraisals(skip: int = 0, limit: int = 100,
                    staff_id: Optional[int] = None,
                    academic_year_id: Optional[int] = None,
                    appraisal_period: Optional[str] = None,
                    db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(TPADAppraisal)
    if staff_id: q = q.filter_by(staff_id=staff_id)
    if academic_year_id: q = q.filter_by(academic_year_id=academic_year_id)
    if appraisal_period: q = q.filter_by(appraisal_period=appraisal_period)
    return q.offset(skip).limit(limit).all()

@router.post("/", response_model=TPADOut, status_code=201)
def create_appraisal(data: TPADCreate, db: Session = Depends(get_db),
                     _=Depends(get_current_user)):
    # One appraisal per staff per period per year
    existing = db.query(TPADAppraisal).filter_by(
        staff_id=data.staff_id,
        academic_year_id=data.academic_year_id,
        appraisal_period=data.appraisal_period,
    ).first()
    if existing:
        raise HTTPException(409, "Appraisal already exists for this period")
    obj = TPADAppraisal(**data.model_dump())
    _recalculate(obj)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/{id}", response_model=TPADOut)
def get_appraisal(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(TPADAppraisal).get(id)
    if not obj: raise HTTPException(404, "Appraisal not found")
    return obj

@router.put("/{id}", response_model=TPADOut)
def update_appraisal(id: int, data: TPADUpdate, db: Session = Depends(get_db),
                     _=Depends(get_current_user)):
    obj = db.query(TPADAppraisal).get(id)
    if not obj: raise HTTPException(404, "Appraisal not found")
    if obj.is_submitted:
        raise HTTPException(400, "Cannot edit a submitted appraisal")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    _recalculate(obj)
    db.commit(); db.refresh(obj)
    return obj

@router.put("/{id}/submit")
def submit_appraisal(id: int, db: Session = Depends(get_db),
                     _=Depends(get_current_user)):
    obj = db.query(TPADAppraisal).get(id)
    if not obj: raise HTTPException(404, "Appraisal not found")
    if obj.is_submitted:
        raise HTTPException(400, "Already submitted")
    _recalculate(obj)
    obj.is_submitted = True
    obj.submitted_at = datetime.utcnow()
    db.commit()
    return {"id": obj.id, "average_score": obj.average_score,
            "rating": obj.rating, "submitted_at": obj.submitted_at}

@router.put("/{id}/acknowledge")
def acknowledge_appraisal(id: int, staff_comments: Optional[str] = None,
                           db: Session = Depends(get_db),
                           current_user=Depends(get_current_user)):
    obj = db.query(TPADAppraisal).get(id)
    if not obj: raise HTTPException(404, "Appraisal not found")
    if not obj.is_submitted:
        raise HTTPException(400, "Appraisal must be submitted before acknowledgement")
    obj.is_acknowledged = True
    obj.acknowledged_at = datetime.utcnow()
    if staff_comments:
        obj.staff_comments = staff_comments
    db.commit()
    return {"id": obj.id, "acknowledged_at": obj.acknowledged_at}

@router.get("/staff/{staff_id}/summary")
def staff_appraisal_summary(staff_id: int, db: Session = Depends(get_db),
                             _=Depends(get_current_user)):
    appraisals = db.query(TPADAppraisal).filter_by(
        staff_id=staff_id, is_submitted=True).all()
    if not appraisals:
        return {"staff_id": staff_id, "appraisals": 0}
    avg = sum(a.average_score for a in appraisals) / len(appraisals)
    return {
        "staff_id": staff_id,
        "total_appraisals": len(appraisals),
        "overall_average": round(avg, 2),
        "overall_rating": _compute_rating(avg),
        "history": [{"id": a.id, "period": a.appraisal_period,
                     "average": a.average_score, "rating": a.rating} for a in appraisals],
    }
