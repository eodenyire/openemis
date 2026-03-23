from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from app.models.student import Gender, BloodGroup


class StudentBase(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    gender: Optional[Gender] = None
    date_of_birth: Optional[date] = None
    blood_group: Optional[BloodGroup] = None
    nationality: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None


class StudentCreate(StudentBase):
    admission_number: str
    course_id: Optional[int] = None
    batch_id: Optional[int] = None


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    course_id: Optional[int] = None


class StudentResponse(StudentBase):
    id: int
    admission_number: str
    course_id: Optional[int] = None
    batch_id: Optional[int] = None

    class Config:
        from_attributes = True
