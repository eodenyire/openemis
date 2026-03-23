"""DigiGuide / Career guidance endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.extras import OpCareer, OpCareerMatch

router = APIRouter()


@router.get("/careers")
def list_careers(cluster: Optional[str] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpCareer).filter_by(active=True)
    if cluster: q = q.filter_by(cluster=cluster)
    return q.all()

@router.post("/careers", status_code=201)
def create_career(name: str, cluster: Optional[str] = None, min_grade: Optional[str] = None,
                  description: Optional[str] = None,
                  db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpCareer(name=name, cluster=cluster, min_grade=min_grade, description=description)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/careers/{id}")
def get_career(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpCareer).get(id)
    if not obj: raise HTTPException(404, "Career not found")
    return obj


@router.get("/career-matches")
def list_matches(student_id: Optional[int] = None, recommended: Optional[bool] = None,
                 db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpCareerMatch)
    if student_id: q = q.filter_by(student_id=student_id)
    if recommended is not None: q = q.filter_by(recommended=recommended)
    return q.all()

@router.post("/career-matches", status_code=201)
def create_match(student_id: int, career_id: int, match_score: Optional[float] = None,
                 recommended: bool = False,
                 db: Session = Depends(get_db), _=Depends(require_admin)):
    existing = db.query(OpCareerMatch).filter_by(student_id=student_id, career_id=career_id).first()
    if existing:
        existing.match_score = match_score
        existing.recommended = recommended
        db.commit(); db.refresh(existing); return existing
    obj = OpCareerMatch(student_id=student_id, career_id=career_id,
                        match_score=match_score, recommended=recommended)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/students/{student_id}/career-recommendations")
def get_student_recommendations(student_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    matches = db.query(OpCareerMatch).filter_by(student_id=student_id, recommended=True).all()
    return matches
