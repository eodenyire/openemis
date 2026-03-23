from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class AttendanceRegisterBase(BaseModel):
    name: str
    course_id: int
    batch_id: Optional[int] = None
    subject_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    academic_term_id: Optional[int] = None

class AttendanceRegisterCreate(AttendanceRegisterBase): pass
class AttendanceRegisterUpdate(BaseModel):
    name: Optional[str] = None
class AttendanceRegisterOut(AttendanceRegisterBase):
    id: int
    class Config: from_attributes = True


class AttendanceLineBase(BaseModel):
    student_id: int
    status: str = "present"
    note: Optional[str] = None

class AttendanceLineCreate(AttendanceLineBase): pass
class AttendanceLineOut(AttendanceLineBase):
    id: int
    class Config: from_attributes = True


class AttendanceSheetBase(BaseModel):
    register_id: int
    attendance_date: date
    faculty_id: Optional[int] = None
    note: Optional[str] = None

class AttendanceSheetCreate(AttendanceSheetBase):
    lines: Optional[List[AttendanceLineCreate]] = []

class AttendanceSheetUpdate(BaseModel):
    state: Optional[str] = None
    note: Optional[str] = None

class AttendanceSheetOut(AttendanceSheetBase):
    id: int
    state: str
    lines: List[AttendanceLineOut] = []
    class Config: from_attributes = True
