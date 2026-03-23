from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class FeesElementBase(BaseModel):
    name: str
    amount: float

class FeesTermLineBase(BaseModel):
    name: str
    due_date: Optional[date] = None
    due_days: Optional[int] = None
    percentage: Optional[float] = None
    amount: Optional[float] = None
    elements: Optional[List[FeesElementBase]] = []

class FeesTermBase(BaseModel):
    name: str
    code: Optional[str] = None
    note: Optional[str] = None

class FeesTermCreate(FeesTermBase):
    lines: Optional[List[FeesTermLineBase]] = []

class FeesTermUpdate(BaseModel):
    name: Optional[str] = None
    note: Optional[str] = None

class FeesElementOut(FeesElementBase):
    id: int
    class Config: from_attributes = True

class FeesTermLineOut(FeesTermLineBase):
    id: int
    elements: List[FeesElementOut] = []
    class Config: from_attributes = True

class FeesTermOut(FeesTermBase):
    id: int
    lines: List[FeesTermLineOut] = []
    class Config: from_attributes = True


class InvoiceBase(BaseModel):
    student_id: int
    course_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    academic_term_id: Optional[int] = None
    fees_term_id: Optional[int] = None
    total_amount: float
    due_date: Optional[date] = None
    note: Optional[str] = None

class InvoiceCreate(InvoiceBase): pass
class InvoiceUpdate(BaseModel):
    state: Optional[str] = None
    note: Optional[str] = None
class InvoiceOut(InvoiceBase):
    id: int
    paid_amount: float
    state: str
    class Config: from_attributes = True


class PaymentBase(BaseModel):
    invoice_id: int
    amount: float
    payment_date: date
    payment_method: Optional[str] = None
    reference: Optional[str] = None
    note: Optional[str] = None

class PaymentCreate(PaymentBase): pass
class PaymentOut(PaymentBase):
    id: int
    class Config: from_attributes = True
