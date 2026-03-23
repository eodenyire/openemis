"""Timetable / Session models — translated from openeducat_timetable."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class SessionState(str, enum.Enum):
    draft = "draft"
    confirm = "confirm"
    done = "done"
    cancel = "cancel"


class OpTimetableRoom(Base):
    """Simplified room reference for timetable sessions (use OpClassroom from facilities for full detail)."""
    __tablename__ = "op_timetable_rooms"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    capacity = Column(Integer, default=0)
    building = Column(String(64))
    floor = Column(String(16))
    active = Column(Boolean, default=True)


class OpTiming(Base):
    __tablename__ = "op_timings"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    start_time = Column(String(8))  # HH:MM
    end_time = Column(String(8))


class OpSession(Base):
    __tablename__ = "op_sessions"
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    timing_id = Column(Integer, ForeignKey("op_timings.id"))
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    course_id = Column(Integer, ForeignKey("op_courses.id"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("op_faculty.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("op_batches.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("op_subjects.id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("op_timetable_rooms.id"))
    days = Column(String(16))  # monday..sunday
    state = Column(SAEnum(SessionState), default=SessionState.draft)
    active = Column(Boolean, default=True)
    timing = relationship("OpTiming")
    course = relationship("OpCourse")
    faculty = relationship("OpFaculty")
    batch = relationship("OpBatch")
    subject = relationship("OpSubject")
    classroom = relationship("OpTimetableRoom")
