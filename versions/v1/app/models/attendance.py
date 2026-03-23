"""Attendance module models"""
import enum
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LEAVE = "leave"
    LATE = "late"


class AttendanceSheetState(str, enum.Enum):
    DRAFT = "draft"
    START = "start"
    DONE = "done"
    CANCEL = "cancel"


class AttendanceRegister(Base):
    __tablename__ = "attendance_registers"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    academic_term_id = Column(Integer, ForeignKey("academic_terms.id"))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course")
    batch = relationship("Batch")
    subject = relationship("Subject")
    sheets = relationship("AttendanceSheet", back_populates="register")


class AttendanceSheet(Base):
    __tablename__ = "attendance_sheets"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    register_id = Column(Integer, ForeignKey("attendance_registers.id"), nullable=False)
    attendance_date = Column(Date, nullable=False)
    faculty_id = Column(Integer, ForeignKey("teachers.id"))
    state = Column(Enum(AttendanceSheetState), default=AttendanceSheetState.DRAFT)
    note = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    register = relationship("AttendanceRegister", back_populates="sheets")
    faculty = relationship("Teacher")
    lines = relationship("AttendanceLine", back_populates="sheet", cascade="all, delete-orphan")


class AttendanceLine(Base):
    __tablename__ = "attendance_lines"
    id = Column(Integer, primary_key=True)
    sheet_id = Column(Integer, ForeignKey("attendance_sheets.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.PRESENT)
    note = Column(String(255))

    sheet = relationship("AttendanceSheet", back_populates="lines")
    student = relationship("Student")
