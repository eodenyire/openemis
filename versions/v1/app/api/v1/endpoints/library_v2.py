"""
Library v2 — enhanced endpoints: issue/return workflow, fine calculation,
overdue tracking, availability search, student borrowing history.
"""
from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.library import Media, MediaMovement, MediaMovementState

router = APIRouter()

FINE_PER_DAY = 5  # KES 5 per day overdue


# ── Schemas ───────────────────────────────────────────────────────────────────

class IssueRequest(BaseModel):
    media_id: int
    student_id: int
    due_date: date
    note: Optional[str] = None

class ReturnRequest(BaseModel):
    note: Optional[str] = None

class MovementOut(BaseModel):
    id: int
    media_id: int
    student_id: int
    issue_date: date
    due_date: Optional[date]
    return_date: Optional[date]
    state: str
    fine: int
    note: Optional[str]
    class Config: from_attributes = True


# ── Issue a book ──────────────────────────────────────────────────────────────

@router.post("/issue", response_model=MovementOut, status_code=201)
def issue_book(data: IssueRequest, db: Session = Depends(get_db),
               _=Depends(get_current_user)):
    media = db.query(Media).get(data.media_id)
    if not media:
        raise HTTPException(404, "Book not found")
    if media.available_copies < 1:
        raise HTTPException(400, f"No copies available for '{media.name}'")
    # Check student doesn't already have this book
    active = db.query(MediaMovement).filter_by(
        media_id=data.media_id, student_id=data.student_id,
        state=MediaMovementState.ISSUED).first()
    if active:
        raise HTTPException(409, "Student already has this book issued")

    movement = MediaMovement(
        media_id=data.media_id,
        student_id=data.student_id,
        issue_date=date.today(),
        due_date=data.due_date,
        state=MediaMovementState.ISSUED,
        note=data.note,
    )
    media.available_copies -= 1
    db.add(movement); db.commit(); db.refresh(movement)
    return movement


@router.put("/return/{movement_id}", response_model=MovementOut)
def return_book(movement_id: int, data: ReturnRequest,
                db: Session = Depends(get_db), _=Depends(get_current_user)):
    movement = db.query(MediaMovement).get(movement_id)
    if not movement:
        raise HTTPException(404, "Movement not found")
    if movement.state == MediaMovementState.RETURNED:
        raise HTTPException(400, "Book already returned")

    today = date.today()
    movement.return_date = today
    movement.state = MediaMovementState.RETURNED

    # Calculate fine
    if movement.due_date and today > movement.due_date:
        overdue_days = (today - movement.due_date).days
        movement.fine = overdue_days * FINE_PER_DAY
    else:
        movement.fine = 0

    if data.note:
        movement.note = data.note

    # Restore copy
    media = db.query(Media).get(movement.media_id)
    if media:
        media.available_copies = min(media.available_copies + 1, media.total_copies)

    db.commit(); db.refresh(movement)
    return movement


@router.put("/lost/{movement_id}")
def mark_lost(movement_id: int, db: Session = Depends(get_db),
              _=Depends(require_admin)):
    movement = db.query(MediaMovement).get(movement_id)
    if not movement:
        raise HTTPException(404, "Movement not found")
    movement.state = MediaMovementState.LOST
    movement.fine = 500  # replacement cost KES 500
    db.commit()
    return {"id": movement.id, "state": movement.state, "fine": movement.fine}


# ── Overdue tracking ──────────────────────────────────────────────────────────

@router.get("/overdue", response_model=List[MovementOut])
def list_overdue(db: Session = Depends(get_db), _=Depends(get_current_user)):
    today = date.today()
    overdue = (db.query(MediaMovement)
               .filter(MediaMovement.state == MediaMovementState.ISSUED)
               .filter(MediaMovement.due_date < today)
               .all())
    # Update state to overdue
    for m in overdue:
        m.state = MediaMovementState.OVERDUE
        m.fine = (today - m.due_date).days * FINE_PER_DAY
    db.commit()
    return overdue


@router.post("/overdue/update-fines")
def update_all_fines(db: Session = Depends(get_db), _=Depends(require_admin)):
    """Recalculate fines for all overdue books."""
    today = date.today()
    overdue = (db.query(MediaMovement)
               .filter(MediaMovement.state.in_([
                   MediaMovementState.ISSUED, MediaMovementState.OVERDUE]))
               .filter(MediaMovement.due_date < today)
               .all())
    updated = 0
    for m in overdue:
        m.state = MediaMovementState.OVERDUE
        m.fine = (today - m.due_date).days * FINE_PER_DAY
        updated += 1
    db.commit()
    return {"updated": updated, "total_fines": sum(m.fine for m in overdue)}


# ── Student borrowing history ─────────────────────────────────────────────────

@router.get("/student/{student_id}/history", response_model=List[MovementOut])
def student_history(student_id: int, db: Session = Depends(get_db),
                    _=Depends(get_current_user)):
    return (db.query(MediaMovement)
            .filter_by(student_id=student_id)
            .order_by(MediaMovement.issue_date.desc())
            .all())


@router.get("/student/{student_id}/active", response_model=List[MovementOut])
def student_active_books(student_id: int, db: Session = Depends(get_db),
                         _=Depends(get_current_user)):
    return db.query(MediaMovement).filter_by(
        student_id=student_id, state=MediaMovementState.ISSUED).all()


# ── Availability search ───────────────────────────────────────────────────────

@router.get("/search")
def search_books(q: Optional[str] = None, available_only: bool = False,
                 grade_level: Optional[str] = None,
                 subject_area: Optional[str] = None,
                 skip: int = 0, limit: int = 50,
                 db: Session = Depends(get_db), _=Depends(get_current_user)):
    query = db.query(Media).filter_by(active=True)
    if q:
        query = query.filter(Media.name.ilike(f"%{q}%"))
    if available_only:
        query = query.filter(Media.available_copies > 0)
    if grade_level:
        query = query.filter_by(grade_level=grade_level)
    if subject_area:
        query = query.filter(Media.subject_area.ilike(f"%{subject_area}%"))
    books = query.offset(skip).limit(limit).all()
    return [
        {"id": b.id, "name": b.name, "isbn": b.isbn,
         "available_copies": b.available_copies, "total_copies": b.total_copies,
         "grade_level": b.grade_level, "subject_area": b.subject_area}
        for b in books
    ]


# ── Library summary ───────────────────────────────────────────────────────────

@router.get("/summary")
def library_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    today = date.today()
    total_books = db.query(Media).filter_by(active=True).count()
    total_copies = db.query(Media).with_entities(
        Media.total_copies).filter_by(active=True).all()
    available = db.query(Media).with_entities(
        Media.available_copies).filter_by(active=True).all()
    issued = db.query(MediaMovement).filter_by(state=MediaMovementState.ISSUED).count()
    overdue_count = (db.query(MediaMovement)
                     .filter(MediaMovement.state.in_([
                         MediaMovementState.ISSUED, MediaMovementState.OVERDUE]))
                     .filter(MediaMovement.due_date < today).count())
    total_fines = db.query(MediaMovement).with_entities(
        MediaMovement.fine).filter(MediaMovement.fine > 0).all()
    return {
        "total_titles": total_books,
        "total_copies": sum(r[0] or 0 for r in total_copies),
        "available_copies": sum(r[0] or 0 for r in available),
        "currently_issued": issued,
        "overdue_books": overdue_count,
        "total_fines_kes": sum(r[0] or 0 for r in total_fines),
    }
