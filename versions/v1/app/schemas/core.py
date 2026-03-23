from pydantic import BaseModel
from typing import Optional
from datetime import date


class DepartmentBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class DepartmentCreate(DepartmentBase): pass
class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
class DepartmentOut(DepartmentBase):
    id: int
    class Config: from_attributes = True


class ProgramLevelBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None

class ProgramLevelCreate(ProgramLevelBase): pass
class ProgramLevelUpdate(BaseModel):
    name: Optional[str] = None
class ProgramLevelOut(ProgramLevelBase):
    id: int
    class Config: from_attributes = True


class ProgramBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    department_id: Optional[int] = None
    program_level_id: Optional[int] = None
    max_unit_load: Optional[float] = None
    min_unit_load: Optional[float] = None

class ProgramCreate(ProgramBase): pass
class ProgramUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
class ProgramOut(ProgramBase):
    id: int
    class Config: from_attributes = True


class CourseBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    department_id: Optional[int] = None
    program_id: Optional[int] = None
    evaluation_type: Optional[str] = "normal"
    duration_years: Optional[int] = None

class CourseCreate(CourseBase): pass
class CourseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    evaluation_type: Optional[str] = None
class CourseOut(CourseBase):
    id: int
    class Config: from_attributes = True


class BatchBase(BaseModel):
    name: str
    code: str
    course_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class BatchCreate(BatchBase): pass
class BatchUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
class BatchOut(BatchBase):
    id: int
    class Config: from_attributes = True


class SubjectBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    credits: Optional[int] = None
    type: Optional[str] = "theory"
    subject_type: Optional[str] = "compulsory"
    department_id: Optional[int] = None

class SubjectCreate(SubjectBase): pass
class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None
class SubjectOut(SubjectBase):
    id: int
    class Config: from_attributes = True


class AcademicYearBase(BaseModel):
    name: str
    code: str
    start_date: date
    end_date: date
    is_current: Optional[bool] = False

class AcademicYearCreate(AcademicYearBase): pass
class AcademicYearUpdate(BaseModel):
    name: Optional[str] = None
    is_current: Optional[bool] = None
class AcademicYearOut(AcademicYearBase):
    id: int
    class Config: from_attributes = True


class AcademicTermBase(BaseModel):
    name: str
    code: str
    start_date: date
    end_date: date
    is_current: Optional[bool] = False
    academic_year_id: int

class AcademicTermCreate(AcademicTermBase): pass
class AcademicTermUpdate(BaseModel):
    name: Optional[str] = None
    is_current: Optional[bool] = None
class AcademicTermOut(AcademicTermBase):
    id: int
    class Config: from_attributes = True


class StudentCategoryBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None

class StudentCategoryCreate(StudentCategoryBase): pass
class StudentCategoryUpdate(BaseModel):
    name: Optional[str] = None
class StudentCategoryOut(StudentCategoryBase):
    id: int
    class Config: from_attributes = True
