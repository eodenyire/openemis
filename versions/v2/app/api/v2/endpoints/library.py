"""Library endpoints."""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.support import OpLibraryBook, OpLibraryMovement

router = APIRouter()


@router.get("/library/books")
def list_books(search: Optional[str] = None, category: Optional[str] = None,
               skip: int = 0, limit: int = 100,
               db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpLibraryBook).filter_by(active=True)
    if search:
        q = q.filter(OpLibraryBook.name.ilike(f"%{search}%") | OpLibraryBook.author.ilike(f"%{search}%"))
    if category: q = q.filter_by(category=category)
    return {"total": q.count(), "items": q.offset(skip).limit(limit).all()}

@router.post("/library/books", status_code=201)
def create_book(name: str, isbn: Optional[str] = None, author: Optional[str] = None,
                publisher: Optional[str] = None, edition: Optional[str] = None,
                total_copies: int = 1, category: Optional[str] = None,
                db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpLibraryBook(name=name, isbn=isbn, author=author, publisher=publisher,
                        edition=edition, total_copies=total_copies, available_copies=total_copies,
                        category=category)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/library/books/{id}")
def get_book(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpLibraryBook).get(id)
    if not obj: raise HTTPException(404, "Book not found")
    return obj


@router.get("/library/movements")
def list_movements(student_id: Optional[int] = None, state: Optional[str] = None,
                   db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpLibraryMovement)
    if student_id: q = q.filter_by(student_id=student_id)
    if state: q = q.filter_by(state=state)
    return q.all()

@router.post("/library/movements", status_code=201)
def issue_book(book_id: int, student_id: int, issue_date: date, due_date: Optional[date] = None,
               db: Session = Depends(get_db), _=Depends(require_admin)):
    book = db.query(OpLibraryBook).get(book_id)
    if not book: raise HTTPException(404, "Book not found")
    if book.available_copies < 1: raise HTTPException(400, "No copies available")
    book.available_copies -= 1
    obj = OpLibraryMovement(book_id=book_id, student_id=student_id, issue_date=issue_date,
                             due_date=due_date, state="issued")
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.patch("/library/movements/{id}/return")
def return_book(id: int, return_date: Optional[date] = None,
                db: Session = Depends(get_db), _=Depends(require_admin)):
    movement = db.query(OpLibraryMovement).get(id)
    if not movement: raise HTTPException(404, "Movement not found")
    if movement.state == "returned": raise HTTPException(400, "Already returned")
    movement.return_date = return_date or date.today()
    movement.state = "returned"
    book = db.query(OpLibraryBook).get(movement.book_id)
    if book: book.available_copies += 1
    db.commit(); db.refresh(movement); return movement
