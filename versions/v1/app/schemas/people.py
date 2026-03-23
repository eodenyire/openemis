from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class TeacherBase(BaseModel):
    employee_id: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    blood_group: Optional[str] = None
    nationality: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    join_date: Optional[date] = None
    main_department_id: Optional[int] = None

class TeacherCreate(TeacherBase): pass
class TeacherUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
class TeacherOut(TeacherBase):
    id: int
    class Config: from_attributes = True


class StudentBase(BaseModel):
    admission_number: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    blood_group: Optional[str] = None
    nationality: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    category_id: Optional[int] = None
    admission_date: Optional[date] = None

class StudentCreate(StudentBase): pass
class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    category_id: Optional[int] = None
class StudentOut(StudentBase):
    id: int
    class Config: from_attributes = True


class StudentCourseBase(BaseModel):
    student_id: int
    course_id: int
    batch_id: Optional[int] = None
    roll_number: Optional[str] = None
    academic_year_id: Optional[int] = None
    academic_term_id: Optional[int] = None
    state: Optional[str] = "running"

class StudentCourseCreate(StudentCourseBase): pass
class StudentCourseUpdate(BaseModel):
    batch_id: Optional[int] = None
    roll_number: Optional[str] = None
    state: Optional[str] = None
class StudentCourseOut(StudentCourseBase):
    id: int
    class Config: from_attributes = True


class ParentBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    phone: Optional[str] = None
    relationship_id: Optional[int] = None

class ParentCreate(ParentBase): pass
class ParentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
class ParentOut(ParentBase):
    id: int
    class Config: from_attributes = True


class ParentRelationshipBase(BaseModel):
    name: str

class ParentRelationshipCreate(ParentRelationshipBase): pass
class ParentRelationshipOut(ParentRelationshipBase):
    id: int
    class Config: from_attributes = True
