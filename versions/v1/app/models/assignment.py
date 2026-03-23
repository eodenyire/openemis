"""Assignment module models"""
import enum
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Enum, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class AssignmentState(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    FINISHED = "finished"
    CANCEL = "cancel"


class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    issued_date = Column(Date, nullable=False)
    submission_date = Column(Date, nullable=False)
    total_marks = Column(Float, nullable=False)
    description = Column(Text)
    state = Column(Enum(AssignmentState), default=AssignmentState.DRAFT)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course")
    batch = relationship("Batch")
    subject = relationship("Subject")
    faculty = relationship("Teacher")
    submissions = relationship("AssignmentSubmission", back_populates="assignment",
                               cascade="all, delete-orphan")


class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    submission_date = Column(Date)
    marks = Column(Float)
    feedback = Column(Text)
    file_url = Column(String)
    state = Column(String(20), default="submitted")   # submitted | graded | late

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("Student")
