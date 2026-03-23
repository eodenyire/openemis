"""Admission models — translated from openeducat_admission."""
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Float, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class AdmissionState(str, enum.Enum):
    draft = "draft"
    submit = "submit"
    confirm = "confirm"
    admission = "admission"
    reject = "reject"
    pending = "pending"
    cancel = "cancel"
    done = "done"


class OpAdmissionRegister(Base):
    __tablename__ = "op_admission_registers"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    course_id = Column(Integer, ForeignKey("op_courses.id"))
    program_id = Column(Integer, ForeignKey("op_programs.id"))
    academic_year_id = Column(Integer, ForeignKey("op_academic_years.id"))
    academic_term_id = Column(Integer, ForeignKey("op_academic_terms.id"))
    min_count = Column(Integer, default=0)
    max_count = Column(Integer, default=0)
    minimum_age = Column(Integer, default=0)
    state = Column(String(16), default="draft")
    active = Column(Boolean, default=True)
    course = relationship("OpCourse")
    admissions = relationship("OpAdmission", back_populates="register")


class OpAdmission(Base):
    __tablename__ = "op_admissions"
    id = Column(Integer, primary_key=True)
    application_number = Column(String(16), unique=True)
    name = Column(String(256), nullable=False)
    first_name = Column(String(64), nullable=False)
    middle_name = Column(String(64))
    last_name = Column(String(64), nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String(8), nullable=False)
    email = Column(String(128), nullable=False)
    phone = Column(String(20))
    mobile = Column(String(20))
    street = Column(String(256))
    city = Column(String(64))
    zip = Column(String(8))
    country = Column(String(64))
    course_id = Column(Integer, ForeignKey("op_courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("op_batches.id"))
    register_id = Column(Integer, ForeignKey("op_admission_registers.id"))
    student_id = Column(Integer, ForeignKey("op_students.id"))
    fees = Column(Float, default=0)
    state = Column(SAEnum(AdmissionState), default=AdmissionState.draft)
    application_date = Column(DateTime, default=datetime.utcnow)
    admission_date = Column(Date)
    due_date = Column(Date)
    prev_institute = Column(String(256))
    prev_course = Column(String(128))
    prev_result = Column(String(128))
    family_income = Column(Float, default=0)
    note = Column(Text)
    active = Column(Boolean, default=True)
    course = relationship("OpCourse")
    batch = relationship("OpBatch")
    register = relationship("OpAdmissionRegister", back_populates="admissions")
    student = relationship("OpStudent")
