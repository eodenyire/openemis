"""Admission module models"""
import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    ForeignKey, Float, Text, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.core import Gender


class AdmissionState(str, enum.Enum):
    DRAFT = "draft"
    SUBMIT = "submit"
    CONFIRM = "confirm"
    ADMISSION = "admission"
    REJECT = "reject"
    CANCEL = "cancel"
    DONE = "done"


class Admission(Base):
    __tablename__ = "admissions"
    id = Column(Integer, primary_key=True)
    application_number = Column(String(50), unique=True, index=True, nullable=False)
    application_date = Column(DateTime, nullable=False, server_default=func.now())
    admission_date = Column(Date)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    last_name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum(Gender))
    email = Column(String(200), nullable=False)
    phone = Column(String(20))
    mobile = Column(String(20))
    street = Column(String(255))
    city = Column(String(100))
    zip = Column(String(20))
    country = Column(String(100))
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    program_id = Column(Integer, ForeignKey("programs.id"))
    prev_institute = Column(String(200))
    prev_result = Column(String(100))
    family_income = Column(Float)
    fees = Column(Float)
    discount = Column(Float, default=0)
    state = Column(Enum(AdmissionState), default=AdmissionState.DRAFT)
    due_date = Column(Date)
    student_id = Column(Integer, ForeignKey("students.id"))
    image = Column(String)
    note = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    course = relationship("Course")
    batch = relationship("Batch")
    program = relationship("Program")
    student = relationship("Student")


class AdmissionRegister(Base):
    __tablename__ = "admission_registers"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    minimum_age = Column(Integer)
    max_count = Column(Integer)
    course_id = Column(Integer, ForeignKey("courses.id"))
    program_id = Column(Integer, ForeignKey("programs.id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    academic_term_id = Column(Integer, ForeignKey("academic_terms.id"))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course")
    program = relationship("Program")
    academic_year = relationship("AcademicYear")
    academic_term = relationship("AcademicTerm")
