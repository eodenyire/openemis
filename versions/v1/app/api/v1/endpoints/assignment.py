from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin, require_teacher
from app.api.crud import get_one, get_all, create_obj, update_obj, delete_obj
from app.models.assignment import Assignment, AssignmentSubmission
from app.schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentOut,
    AssignmentSubmissionCreate, AssignmentSubmissionUpdate, AssignmentSubmissionOut,
)

router = APIRouter()


@router.get("/", response_model=List[AssignmentOut], tags=["Assignments"])
def list_assignments(skip: int = 0, limit: int = 100, course_id: int = None,
                     subject_id: int = None, db: Session = Depends(get_db),
                     _=Depends(get_current_user)):
    q = db.query(Assignment)
    if course_id: q = q.filter(Assignment.course_id == course_id)
    if subject_id: q = q.filter(Assignment.subject_id == subject_id)
    return q.offset(skip).limit(limit).all()

@router.post("/", response_model=AssignmentOut, status_code=201, tags=["Assignments"])
def create_assignment(data: AssignmentCreate, db: Session = Depends(get_db),
                      _=Depends(require_teacher)):
    return create_obj(db, Assignment, data.model_dump())

@router.get("/{id}", response_model=AssignmentOut, tags=["Assignments"])
def get_assignment(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, Assignment, id)
    if not obj: raise HTTPException(404, "Assignment not found")
    return obj

@router.put("/{id}", response_model=AssignmentOut, tags=["Assignments"])
def update_assignment(id: int, data: AssignmentUpdate, db: Session = Depends(get_db),
                      _=Depends(require_teacher)):
    obj = get_one(db, Assignment, id)
    if not obj: raise HTTPException(404, "Assignment not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.post("/{id}/publish", response_model=AssignmentOut, tags=["Assignments"])
def publish_assignment(id: int, db: Session = Depends(get_db), _=Depends(require_teacher)):
    obj = get_one(db, Assignment, id)
    if not obj: raise HTTPException(404, "Assignment not found")
    return update_obj(db, obj, {"state": "published"})

@router.post("/{id}/close", response_model=AssignmentOut, tags=["Assignments"])
def close_assignment(id: int, db: Session = Depends(get_db), _=Depends(require_teacher)):
    obj = get_one(db, Assignment, id)
    if not obj: raise HTTPException(404, "Assignment not found")
    return update_obj(db, obj, {"state": "finished"})

@router.delete("/{id}", status_code=204, tags=["Assignments"])
def delete_assignment(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Assignment, id)
    if not obj: raise HTTPException(404, "Assignment not found")
    delete_obj(db, obj)


# ── Submissions ───────────────────────────────────────────────────────────────
@router.get("/{assignment_id}/submissions", response_model=List[AssignmentSubmissionOut], tags=["Assignments"])
def list_submissions(assignment_id: int, db: Session = Depends(get_db),
                     _=Depends(get_current_user)):
    return db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id).all()

@router.post("/{assignment_id}/submissions", response_model=AssignmentSubmissionOut,
             status_code=201, tags=["Assignments"])
def submit_assignment(assignment_id: int, data: AssignmentSubmissionCreate,
                      db: Session = Depends(get_db), _=Depends(get_current_user)):
    payload = data.model_dump()
    payload["assignment_id"] = assignment_id
    return create_obj(db, AssignmentSubmission, payload)

@router.put("/submissions/{id}", response_model=AssignmentSubmissionOut, tags=["Assignments"])
def grade_submission(id: int, data: AssignmentSubmissionUpdate,
                     db: Session = Depends(get_db), _=Depends(require_teacher)):
    obj = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == id).first()
    if not obj: raise HTTPException(404, "Submission not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))
