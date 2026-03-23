from pydantic import BaseModel
from typing import Optional
from datetime import datetime, time


class TimingBase(BaseModel):
    name: str
    start_time: time
    end_time: time

class TimingCreate(TimingBase): pass
class TimingUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
class TimingOut(TimingBase):
    id: int
    class Config: from_attributes = True


class ClassroomBase(BaseModel):
    name: str
    code: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None

class ClassroomCreate(ClassroomBase): pass
class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
class ClassroomOut(ClassroomBase):
    id: int
    class Config: from_attributes = True


class SessionBase(BaseModel):
    course_id: int
    batch_id: int
    subject_id: int
    faculty_id: int
    start_datetime: datetime
    end_datetime: datetime
    timing_id: Optional[int] = None
    classroom_id: Optional[int] = None
    day: Optional[str] = None

class SessionCreate(SessionBase): pass
class SessionUpdate(BaseModel):
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    classroom_id: Optional[int] = None
    state: Optional[str] = None
class SessionOut(SessionBase):
    id: int
    state: str
    class Config: from_attributes = True
