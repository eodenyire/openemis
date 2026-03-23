from pydantic import BaseModel
from typing import Optional
from datetime import date


class HostelBlockBase(BaseModel):
    name: str
    capacity: Optional[int] = None
class HostelBlockCreate(HostelBlockBase): pass
class HostelBlockOut(HostelBlockBase):
    id: int
    class Config: from_attributes = True

class HostelRoomTypeBase(BaseModel):
    name: str
    monthly_fee: float
    capacity: Optional[int] = 1
class HostelRoomTypeCreate(HostelRoomTypeBase): pass
class HostelRoomTypeOut(HostelRoomTypeBase):
    id: int
    class Config: from_attributes = True

class HostelRoomBase(BaseModel):
    name: str
    block_id: Optional[int] = None
    room_type_id: Optional[int] = None
    capacity: int
class HostelRoomCreate(HostelRoomBase): pass
class HostelRoomUpdate(BaseModel):
    state: Optional[str] = None
    capacity: Optional[int] = None
class HostelRoomOut(HostelRoomBase):
    id: int
    state: str
    class Config: from_attributes = True

class HostelAllocationBase(BaseModel):
    student_id: int
    room_id: int
    academic_year_id: Optional[int] = None
    check_in_date: date
    check_out_date: Optional[date] = None
    notes: Optional[str] = None
class HostelAllocationCreate(HostelAllocationBase): pass
class HostelAllocationUpdate(BaseModel):
    state: Optional[str] = None
    check_out_date: Optional[date] = None
    notes: Optional[str] = None
class HostelAllocationOut(HostelAllocationBase):
    id: int
    state: str
    monthly_fee: Optional[float] = None
    class Config: from_attributes = True
