"""Attendance models — translated from openeducat_attendance."""
from datetime import date
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class OpAttendanceRegister(Base):
    __tablename__ = "op_attendance_registers"
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    code = Column(String(16))
    course_id = Column(Integer, ForeignKey("op_courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("op_batches.id"))
    academic_year_id = Column(Integer, ForeignKey("op_academic_years.id"))
    active = Column(Boolean, default=True)
    course = relationship("OpCourse")
    batch = relationship("OpBatch")
    sheets = relationship("OpAttendanceSheet", back_populates="register")


class OpAttendanceSheet(Base):
    __tablename__ = "op_attendance_sheets"
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    register_id = Column(Integer, ForeignKey("op_attendance_registers.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("op_sessions.id"))
    attendance_date = Column(Date, nullable=False)
    faculty_id = Column(Integer, ForeignKey("op_faculty.id"))
    state = Column(String(16), default="draft")  # draft | start | done | cancel
    active = Column(Boolean, default=True)
    register = relationship("OpAttendanceRegister", back_populates="sheets")
    faculty = relationship("OpFaculty")
    lines = relationship("OpAttendanceLine", back_populates="sheet")


class OpAttendanceLine(Base):
    __tablename__ = "op_attendance_lines"
    id = Column(Integer, primary_key=True)
    sheet_id = Column(Integer, ForeignKey("op_attendance_sheets.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    present = Column(Boolean, default=False)
    absent = Column(Boolean, default=False)
    excused = Column(Boolean, default=False)
    late = Column(Boolean, default=False)
    remark = Column(String(256))
    sheet = relationship("OpAttendanceSheet", back_populates="lines")
    student = relationship("OpStudent")
    __table_args__ = (UniqueConstraint("sheet_id", "student_id", name="uq_attendance_line"),)
