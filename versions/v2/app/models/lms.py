"""LMS models — translated from openeducat_lms."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class OpLmsCourse(Base):
    __tablename__ = "op_lms_courses"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    code = Column(String(16), unique=True, nullable=False)
    description = Column(Text)
    faculty_id = Column(Integer, ForeignKey("op_faculty.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("op_courses.id"))
    subject_id = Column(Integer, ForeignKey("op_subjects.id"))
    state = Column(String(16), default="draft")  # draft | published | archived
    active = Column(Boolean, default=True)
    faculty = relationship("OpFaculty")
    course = relationship("OpCourse")
    subject = relationship("OpSubject")
    sections = relationship("OpLmsSection", back_populates="lms_course", order_by="OpLmsSection.sequence")
    enrollments = relationship("OpLmsEnrollment", back_populates="lms_course")


class OpLmsSection(Base):
    __tablename__ = "op_lms_sections"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    lms_course_id = Column(Integer, ForeignKey("op_lms_courses.id"), nullable=False)
    sequence = Column(Integer, default=1)
    lms_course = relationship("OpLmsCourse", back_populates="sections")
    contents = relationship("OpLmsContent", back_populates="section", order_by="OpLmsContent.sequence")


class OpLmsContent(Base):
    __tablename__ = "op_lms_contents"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    content_type = Column(String(32), default="document")  # document | video | quiz | assignment
    resource_url = Column(String(512))
    section_id = Column(Integer, ForeignKey("op_lms_sections.id"), nullable=False)
    sequence = Column(Integer, default=1)
    active = Column(Boolean, default=True)
    section = relationship("OpLmsSection", back_populates="contents")


class OpLmsEnrollment(Base):
    __tablename__ = "op_lms_enrollments"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    lms_course_id = Column(Integer, ForeignKey("op_lms_courses.id"), nullable=False)
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    completion_percentage = Column(Float, default=0)
    status = Column(String(16), default="enrolled")  # enrolled | in_progress | completed | dropped
    completion_date = Column(DateTime)
    student = relationship("OpStudent")
    lms_course = relationship("OpLmsCourse", back_populates="enrollments")
    __table_args__ = (UniqueConstraint("student_id", "lms_course_id", name="uq_lms_enrollment"),)
