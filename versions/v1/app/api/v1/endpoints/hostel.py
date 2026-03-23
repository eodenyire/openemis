from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.api.crud import get_one, get_all, create_obj, update_obj, delete_obj
from app.models.hostel import HostelBlock, HostelRoomType, HostelRoom, HostelAllocation
from app.schemas.hostel import (
    HostelBlockCreate, HostelBlockOut,
    HostelRoomTypeCreate, HostelRoomTypeOut,
    HostelRoomCreate, HostelRoomUpdate, HostelRoomOut,
    HostelAllocationCreate, HostelAllocationUpdate, HostelAllocationOut,
)

router = APIRouter()

@router.get("/blocks", response_model=List[HostelBlockOut], tags=["Hostel"])
def list_blocks(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, HostelBlock)

@router.post("/blocks", response_model=HostelBlockOut, status_code=201, tags=["Hostel"])
def create_block(data: HostelBlockCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, HostelBlock, data.model_dump())

@router.delete("/blocks/{id}", status_code=204, tags=["Hostel"])
def delete_block(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, HostelBlock, id)
    if not obj: raise HTTPException(404, "Block not found")
    delete_obj(db, obj)

@router.get("/room-types", response_model=List[HostelRoomTypeOut], tags=["Hostel"])
def list_room_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, HostelRoomType)

@router.post("/room-types", response_model=HostelRoomTypeOut, status_code=201, tags=["Hostel"])
def create_room_type(data: HostelRoomTypeCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, HostelRoomType, data.model_dump())

@router.get("/rooms", response_model=List[HostelRoomOut], tags=["Hostel"])
def list_rooms(skip: int = 0, limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, HostelRoom, skip, limit)

@router.post("/rooms", response_model=HostelRoomOut, status_code=201, tags=["Hostel"])
def create_room(data: HostelRoomCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, HostelRoom, data.model_dump())

@router.put("/rooms/{id}", response_model=HostelRoomOut, tags=["Hostel"])
def update_room(id: int, data: HostelRoomUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, HostelRoom, id)
    if not obj: raise HTTPException(404, "Room not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/rooms/{id}", status_code=204, tags=["Hostel"])
def delete_room(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, HostelRoom, id)
    if not obj: raise HTTPException(404, "Room not found")
    delete_obj(db, obj)

@router.get("/allocations", response_model=List[HostelAllocationOut], tags=["Hostel"])
def list_allocations(skip: int = 0, limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, HostelAllocation, skip, limit)

@router.post("/allocations", response_model=HostelAllocationOut, status_code=201, tags=["Hostel"])
def create_allocation(data: HostelAllocationCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    room = get_one(db, HostelRoom, data.room_id)
    if not room: raise HTTPException(404, "Room not found")
    payload = data.model_dump()
    if room.room_type_id:
        rt = get_one(db, HostelRoomType, room.room_type_id)
        if rt: payload["monthly_fee"] = rt.monthly_fee
    return create_obj(db, HostelAllocation, payload)

@router.put("/allocations/{id}", response_model=HostelAllocationOut, tags=["Hostel"])
def update_allocation(id: int, data: HostelAllocationUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, HostelAllocation, id)
    if not obj: raise HTTPException(404, "Allocation not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/allocations/{id}", status_code=204, tags=["Hostel"])
def delete_allocation(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, HostelAllocation, id)
    if not obj: raise HTTPException(404, "Allocation not found")
    delete_obj(db, obj)
