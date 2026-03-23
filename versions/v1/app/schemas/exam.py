from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ExamSessionBase(BaseModel):
    name: str
    course_id: int
    batch_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    academic_term_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ExamSessionCreate(ExamSessionBase): pass
class ExamSessionUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
class ExamSessionOut(ExamSessionBase):
    id: int
    state: str
    class Config: from_attributes = True


class ExamBase(BaseModel):
    name: str
    exam_code: str
    session_id: Optional[int] = None
    course_id: Optional[int] = None
    batch_id: Optional[int] = None
    subject_id: int
    start_time: datetime
    end_time: datetime
    total_marks: int
    min_marks: int
    note: Optional[str] = None

class ExamCreate(ExamBase): pass
class ExamUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    note: Optional[str] = None
class ExamOut(ExamBase):
    id: int
    state: str
    class Config: from_attributes = True


class ExamAttendeeBase(BaseModel):
    exam_id: int
    student_id: int
    marks: Optional[float] = None
    state: Optional[str] = "present"

class ExamAttendeeCreate(ExamAttendeeBase): pass
class ExamAttendeeUpdate(BaseModel):
    marks: Optional[float] = None
    state: Optional[str] = None
class ExamAttendeeOut(ExamAttendeeBase):
    id: int
    class Config: from_attributes = True


class GradingRuleBase(BaseModel):
    name: str
    min_marks: float
    max_marks: float
    grade_point: Optional[float] = None

class GradingConfigBase(BaseModel):
    name: str

class GradingConfigCreate(GradingConfigBase):
    rules: Optional[List[GradingRuleBase]] = []

class GradingConfigUpdate(BaseModel):
    name: Optional[str] = None

class GradingRuleOut(GradingRuleBase):
    id: int
    class Config: from_attributes = True

class GradingConfigOut(GradingConfigBase):
    id: int
    rules: List[GradingRuleOut] = []
    class Config: from_attributes = True
