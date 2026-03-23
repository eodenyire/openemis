"""Exam module models"""
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class ExamState(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    HELD = "held"
    RESULT_UPDATED = "result_updated"
    CANCEL = "cancel"
    DONE = "done"


class ExamSession(Base):
    __tablename__ = "exam_sessions"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    academic_term_id = Column(Integer, ForeignKey("academic_terms.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    state = Column(String(20), default="draft")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course")
    batch = relationship("Batch")
    exams = relationship("Exam", back_populates="session")


class Exam(Base):
    __tablename__ = "exams"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    exam_code = Column(String(50), unique=True, index=True, nullable=False)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    batch_id = Column(Integer, ForeignKey("batches.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    total_marks = Column(Integer, nullable=False)
    min_marks = Column(Integer, nullable=False)   # passing marks
    state = Column(Enum(ExamState), default=ExamState.DRAFT)
    note = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ExamSession", back_populates="exams")
    course = relationship("Course")
    batch = relationship("Batch")
    subject = relationship("Subject")
    attendees = relationship("ExamAttendees", back_populates="exam", cascade="all, delete-orphan")


class ExamAttendees(Base):
    __tablename__ = "exam_attendees"
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    marks = Column(Float)
    state = Column(String(20), default="present")   # present | absent | pass | fail

    exam = relationship("Exam", back_populates="attendees")
    student = relationship("Student")


class GradingConfig(Base):
    __tablename__ = "grading_configs"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    rules = relationship("GradingRule", back_populates="config", cascade="all, delete-orphan")


class GradingRule(Base):
    __tablename__ = "grading_rules"
    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, ForeignKey("grading_configs.id"), nullable=False)
    name = Column(String(50), nullable=False)   # e.g. "A", "B+", "Distinction"
    min_marks = Column(Float, nullable=False)
    max_marks = Column(Float, nullable=False)
    grade_point = Column(Float)

    config = relationship("GradingConfig", back_populates="rules")
