from pydantic import BaseModel
from typing import Optional
from datetime import date


class AssignmentBase(BaseModel):
    name: str
    course_id: int
    batch_id: Optional[int] = None
    subject_id: int
    faculty_id: int
    issued_date: date
    submission_date: date
    total_marks: float
    description: Optional[str] = None

class AssignmentCreate(AssignmentBase): pass
class AssignmentUpdate(BaseModel):
    name: Optional[str] = None
    submission_date: Optional[date] = None
    state: Optional[str] = None
    description: Optional[str] = None
class AssignmentOut(AssignmentBase):
    id: int
    state: str
    class Config: from_attributes = True


class AssignmentSubmissionBase(BaseModel):
    assignment_id: int
    student_id: int
    submission_date: Optional[date] = None
    marks: Optional[float] = None
    feedback: Optional[str] = None
    file_url: Optional[str] = None

class AssignmentSubmissionCreate(AssignmentSubmissionBase): pass
class AssignmentSubmissionUpdate(BaseModel):
    marks: Optional[float] = None
    feedback: Optional[str] = None
    state: Optional[str] = None
class AssignmentSubmissionOut(AssignmentSubmissionBase):
    id: int
    state: str
    class Config: from_attributes = True
