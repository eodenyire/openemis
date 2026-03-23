from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class AdmissionBase(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    birth_date: date
    gender: Optional[str] = None
    email: str
    phone: Optional[str] = None
    mobile: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    course_id: int
    batch_id: Optional[int] = None
    program_id: Optional[int] = None
    prev_institute: Optional[str] = None
    prev_result: Optional[str] = None
    family_income: Optional[float] = None
    fees: Optional[float] = None
    discount: Optional[float] = 0
    note: Optional[str] = None

class AdmissionCreate(AdmissionBase): pass
class AdmissionUpdate(BaseModel):
    state: Optional[str] = None
    admission_date: Optional[date] = None
    batch_id: Optional[int] = None
    note: Optional[str] = None
class AdmissionOut(AdmissionBase):
    id: int
    application_number: str
    state: str
    application_date: datetime
    class Config: from_attributes = True


class AdmissionRegisterBase(BaseModel):
    name: str
    start_date: date
    end_date: date
    minimum_age: Optional[int] = None
    max_count: Optional[int] = None
    course_id: Optional[int] = None
    program_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    academic_term_id: Optional[int] = None

class AdmissionRegisterCreate(AdmissionRegisterBase): pass
class AdmissionRegisterUpdate(BaseModel):
    name: Optional[str] = None
    end_date: Optional[date] = None
    max_count: Optional[int] = None
class AdmissionRegisterOut(AdmissionRegisterBase):
    id: int
    class Config: from_attributes = True
