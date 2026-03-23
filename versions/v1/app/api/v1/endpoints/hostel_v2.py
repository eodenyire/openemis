"""
Hostel v2 — enhanced: occupancy tracking, check-in/out workflow,
room availability, capacity management, hostel summary.
"""
from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.hostel import (
    HostelBlock, HostelRoom, HostelRoomType, HostelAllocation,
    HostelAllocationState,
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class CheckInRequest(BaseModel):
    student_id: int
    room_id: int
    academic_year_id: int
    check_in_date: date
    notes: Optional[str] = None

class CheckOutRequest(BaseModel):
    check_out_date: date
    notes: Optional[str] = None

class AllocationOut(BaseModel):
    id: int; student_id: int; room_id: int
    academic_year_id: Optional[int]
    check_in_date: date; check_out_date: Optional[date]
    monthly_fee: Optional[float]; state: str; notes: Optional[str]
    class Config: from_attributes = True

class RoomOut(BaseModel):
    id: int; name: str; block_id: Optional[int]
    room_type_id: Optional[int]; capacity: int; state: str
    class Config: from_attributes = True


# ── Check-in ──────────────────────────────────────────────────────────────────

@router.post("/check-in", response_model=AllocationOut, status_code=201)
def check_in(data: CheckInRequest, db: Session = Depends(get_db),
             _=Depends(require_admin)):
    room = db.query(HostelRoom).get(data.room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    if room.state == "maintenance":
        raise HTTPException(400, "Room is under maintenance")

    # Check capacity
    active_count = db.query(HostelAllocation).filter_by(
        room_id=data.room_id,
        state=HostelAllocationState.CONFIRMED).count()
    if active_count >= room.capacity:
        raise HTTPException(400, f"Room is full ({room.capacity}/{room.capacity})")

    # Check student not already allocated
    existing = db.query(HostelAllocation).filter_by(
        student_id=data.student_id,
        state=HostelAllocationState.CONFIRMED).first()
    if existing:
        raise HTTPException(409, f"Student already allocated to room {existing.room_id}")

    # Get fee from room type
    monthly_fee = 0.0
    if room.room_type_id:
        rt = db.query(HostelRoomType).get(room.room_type_id)
        if rt:
            monthly_fee = rt.monthly_fee

    allocation = HostelAllocation(
        student_id=data.student_id,
        room_id=data.room_id,
        academic_year_id=data.academic_year_id,
        check_in_date=data.check_in_date,
        monthly_fee=monthly_fee,
        state=HostelAllocationState.CONFIRMED,
        notes=data.notes,
    )
    db.add(allocation); db.flush()

    # Update room state if now full
    new_count = active_count + 1
    if new_count >= room.capacity:
        room.state = "occupied"
    db.commit(); db.refresh(allocation)
    return allocation


@router.put("/check-out/{allocation_id}", response_model=AllocationOut)
def check_out(allocation_id: int, data: CheckOutRequest,
              db: Session = Depends(get_db), _=Depends(require_admin)):
    allocation = db.query(HostelAllocation).get(allocation_id)
    if not allocation:
        raise HTTPException(404, "Allocation not found")
    if allocation.state == HostelAllocationState.CHECKED_OUT:
        raise HTTPException(400, "Already checked out")

    allocation.check_out_date = data.check_out_date
    allocation.state = HostelAllocationState.CHECKED_OUT
    if data.notes:
        allocation.notes = data.notes

    # Free up room
    room = db.query(HostelRoom).get(allocation.room_id)
    if room and room.state == "occupied":
        remaining = db.query(HostelAllocation).filter_by(
            room_id=room.id, state=HostelAllocationState.CONFIRMED).count()
        if remaining <= 1:  # this checkout will make it 0
            room.state = "available"

    db.commit(); db.refresh(allocation)
    return allocation


# ── Room availability ─────────────────────────────────────────────────────────

@router.get("/rooms/available", response_model=List[RoomOut])
def available_rooms(block_id: Optional[int] = None,
                    room_type_id: Optional[int] = None,
                    db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(HostelRoom).filter(HostelRoom.state != "maintenance")
    if block_id: q = q.filter_by(block_id=block_id)
    if room_type_id: q = q.filter_by(room_type_id=room_type_id)
    rooms = q.all()
    available = []
    for room in rooms:
        occupied = db.query(HostelAllocation).filter_by(
            room_id=room.id, state=HostelAllocationState.CONFIRMED).count()
        if occupied < room.capacity:
            available.append(room)
    return available


@router.get("/rooms/{room_id}/occupants")
def room_occupants(room_id: int, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
    room = db.query(HostelRoom).get(room_id)
    if not room: raise HTTPException(404, "Room not found")
    allocations = db.query(HostelAllocation).filter_by(
        room_id=room_id, state=HostelAllocationState.CONFIRMED).all()
    occupied = len(allocations)
    return {
        "room_id": room_id,
        "room_name": room.name,
        "capacity": room.capacity,
        "occupied": occupied,
        "available_beds": room.capacity - occupied,
        "occupants": [
            {"allocation_id": a.id, "student_id": a.student_id,
             "check_in_date": a.check_in_date, "monthly_fee": a.monthly_fee}
            for a in allocations
        ],
    }


@router.get("/student/{student_id}/allocation", response_model=AllocationOut)
def student_allocation(student_id: int, db: Session = Depends(get_db),
                       _=Depends(get_current_user)):
    alloc = db.query(HostelAllocation).filter_by(
        student_id=student_id, state=HostelAllocationState.CONFIRMED).first()
    if not alloc:
        raise HTTPException(404, "No active hostel allocation for this student")
    return alloc


# ── Hostel summary ────────────────────────────────────────────────────────────

@router.get("/summary")
def hostel_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    blocks = db.query(HostelBlock).all()
    total_rooms = db.query(HostelRoom).count()
    total_capacity = sum(r.capacity for r in db.query(HostelRoom).all())
    occupied_students = db.query(HostelAllocation).filter_by(
        state=HostelAllocationState.CONFIRMED).count()
    maintenance_rooms = db.query(HostelRoom).filter_by(state="maintenance").count()

    block_summary = []
    for block in blocks:
        rooms = db.query(HostelRoom).filter_by(block_id=block.id).all()
        block_capacity = sum(r.capacity for r in rooms)
        block_occupied = sum(
            db.query(HostelAllocation).filter_by(
                room_id=r.id, state=HostelAllocationState.CONFIRMED).count()
            for r in rooms
        )
        block_summary.append({
            "block_id": block.id,
            "block_name": block.name,
            "rooms": len(rooms),
            "capacity": block_capacity,
            "occupied": block_occupied,
            "occupancy_rate": round(block_occupied / block_capacity * 100, 1) if block_capacity else 0,
        })

    return {
        "total_rooms": total_rooms,
        "total_capacity": total_capacity,
        "occupied": occupied_students,
        "available_beds": total_capacity - occupied_students,
        "occupancy_rate": round(occupied_students / total_capacity * 100, 1) if total_capacity else 0,
        "maintenance_rooms": maintenance_rooms,
        "blocks": block_summary,
    }


@router.put("/rooms/{room_id}/maintenance")
def toggle_maintenance(room_id: int, in_maintenance: bool,
                       db: Session = Depends(get_db), _=Depends(require_admin)):
    room = db.query(HostelRoom).get(room_id)
    if not room: raise HTTPException(404, "Room not found")
    room.state = "maintenance" if in_maintenance else "available"
    db.commit()
    return {"room_id": room_id, "state": room.state}
