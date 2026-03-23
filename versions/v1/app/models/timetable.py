"""Timetable / Session models"""
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class SessionState(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    DONE = "done"
    CANCEL = "cancel"


class DayOfWeek(str, enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class Timing(Base):
    __tablename__ = "timings"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    active = Column(Boolean, default=True)

    sessions = relationship("Session", back_populates="timing")


class Classroom(Base):
    __tablename__ = "classrooms"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True)
    capacity = Column(Integer)
    location = Column(String(200))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship("Session", back_populates="classroom")


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    timing_id = Column(Integer, ForeignKey("timings.id"))
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))
    day = Column(Enum(DayOfWeek))
    state = Column(Enum(SessionState), default=SessionState.DRAFT)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    timing = relationship("Timing", back_populates="sessions")
    course = relationship("Course")
    batch = relationship("Batch")
    subject = relationship("Subject")
    faculty = relationship("Teacher")
    classroom = relationship("Classroom", back_populates="sessions")
