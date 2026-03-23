"""Hostel endpoints."""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.support import OpHostelBlock, OpHostelRoom, OpHostelAllocation

router = APIRouter()


@router.get("/hostel/blocks")
def list_blocks(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpHostelBlock).filter_by(active=True).all()

@router.post("/hostel/blocks", status_code=201)
def create_block(name: str, gender: Optional[str] = None,
                 db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpHostelBlock(name=name, gender=gender)
    db.add(obj); db.commit(); db.refresh(obj); return obj


@router.get("/hostel/rooms")
def list_rooms(block_id: Optional[int] = None, state: Optional[str] = None,
               db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpHostelRoom).filter_by(active=True)
    if block_id: q = q.filter_by(block_id=block_id)
    if state: q = q.filter_by(state=state)
    return q.all()

@router.post("/hostel/rooms", status_code=201)
def create_room(name: str, block_id: int, capacity: int = 1,
                room_type: Optional[str] = None, monthly_fee: float = 0,
                db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpHostelRoom(name=name, block_id=block_id, capacity=capacity,
                       room_type=room_type, monthly_fee=monthly_fee)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/hostel/rooms/{id}")
def get_room(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpHostelRoom).get(id)
    if not obj: raise HTTPException(404, "Room not found")
    return obj


@router.get("/hostel/allocations")
def list_allocations(student_id: Optional[int] = None, room_id: Optional[int] = None,
                     db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpHostelAllocation)
    if student_id: q = q.filter_by(student_id=student_id)
    if room_id: q = q.filter_by(room_id=room_id)
    return q.all()

@router.post("/hostel/allocations", status_code=201)
def allocate_room(student_id: int, room_id: int, check_in_date: date,
                  academic_year_id: Optional[int] = None,
                  db: Session = Depends(get_db), _=Depends(require_admin)):
    room = db.query(OpHostelRoom).get(room_id)
    if not room: raise HTTPException(404, "Room not found")
    active_count = db.query(OpHostelAllocation).filter_by(room_id=room_id, state="confirmed").count()
    if active_count >= room.capacity:
        raise HTTPException(400, "Room is at full capacity")
    obj = OpHostelAllocation(student_id=student_id, room_id=room_id, check_in_date=check_in_date,
                              academic_year_id=academic_year_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.patch("/hostel/allocations/{id}/checkout")
def checkout(id: int, check_out_date: Optional[date] = None,
             db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpHostelAllocation).get(id)
    if not obj: raise HTTPException(404, "Allocation not found")
    obj.check_out_date = check_out_date or date.today()
    obj.state = "checked_out"
    db.commit(); db.refresh(obj); return obj
