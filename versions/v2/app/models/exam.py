"""Exam models — translated from openeducat_exam."""
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Float, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.base import Base


exam_faculty = Table(
    "op_exam_faculty", Base.metadata,
    Column("exam_id", Integer, ForeignKey("op_exams.id"), primary_key=True),
    Column("faculty_id", Integer, ForeignKey("op_faculty.id"), primary_key=True),
)


class OpExamSession(Base):
    __tablename__ = "op_exam_sessions"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    course_id = Column(Integer, ForeignKey("op_courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("op_batches.id"))
    academic_year_id = Column(Integer, ForeignKey("op_academic_years.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    state = Column(String(16), default="draft")  # draft | schedule | done | cancel
    active = Column(Boolean, default=True)
    course = relationship("OpCourse")
    batch = relationship("OpBatch")
    exams = relationship("OpExam", back_populates="session")


class OpExam(Base):
    __tablename__ = "op_exams"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    exam_code = Column(String(16), unique=True, nullable=False)
    session_id = Column(Integer, ForeignKey("op_exam_sessions.id"))
    subject_id = Column(Integer, ForeignKey("op_subjects.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    total_marks = Column(Integer, nullable=False)
    min_marks = Column(Integer, nullable=False)
    state = Column(String(16), default="draft")
    note = Column(Text)
    active = Column(Boolean, default=True)
    session = relationship("OpExamSession", back_populates="exams")
    subject = relationship("OpSubject")
    responsible = relationship("OpFaculty", secondary=exam_faculty)
    attendees = relationship("OpExamAttendee", back_populates="exam")


class OpExamAttendee(Base):
    __tablename__ = "op_exam_attendees"
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("op_exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    marks = Column(Float)
    status = Column(String(8))  # pass | fail
    exam = relationship("OpExam", back_populates="attendees")
    student = relationship("OpStudent")


class OpMarksheetRegister(Base):
    __tablename__ = "op_marksheet_registers"
    id = Column(Integer, primary_key=True)
    exam_session_id = Column(Integer, ForeignKey("op_exam_sessions.id"), nullable=False)
    generated_date = Column(Date)
    state = Column(String(16), default="draft")
    session = relationship("OpExamSession")
    lines = relationship("OpMarksheetLine", back_populates="register")


class OpMarksheetLine(Base):
    __tablename__ = "op_marksheet_lines"
    id = Column(Integer, primary_key=True)
    register_id = Column(Integer, ForeignKey("op_marksheet_registers.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    marks = Column(Float)
    status = Column(String(8))  # pass | fail
    register = relationship("OpMarksheetRegister", back_populates="lines")
    student = relationship("OpStudent")



