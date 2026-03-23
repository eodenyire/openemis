"""Extra models — activity, achievement, discipline, event, blog, notice, alumni, scholarship, facility."""
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class OpActivity(Base):
    __tablename__ = "op_activities"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    activity_type = Column(String(64))
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    responsible_id = Column(Integer, ForeignKey("op_faculty.id"))
    active = Column(Boolean, default=True)
    responsible = relationship("OpFaculty")


class OpAchievement(Base):
    __tablename__ = "op_achievements"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    name = Column(String(128), nullable=False)
    achievement_type = Column(String(64))
    date = Column(Date)
    description = Column(Text)
    active = Column(Boolean, default=True)
    student = relationship("OpStudent")


class OpDisciplineRecord(Base):
    __tablename__ = "op_discipline_records"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    incident_date = Column(Date, nullable=False)
    incident_type = Column(String(64))
    description = Column(Text)
    action_taken = Column(Text)
    reported_by_id = Column(Integer, ForeignKey("op_faculty.id"))
    state = Column(String(16), default="open")
    active = Column(Boolean, default=True)
    student = relationship("OpStudent")
    reported_by = relationship("OpFaculty")


class OpEvent(Base):
    __tablename__ = "op_events"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    event_type = Column(String(64))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    location = Column(String(256))
    description = Column(Text)
    max_participants = Column(Integer)
    active = Column(Boolean, default=True)
    registrations = relationship("OpEventRegistration", back_populates="event")


class OpEventRegistration(Base):
    __tablename__ = "op_event_registrations"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("op_events.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    status = Column(String(16), default="registered")
    event = relationship("OpEvent", back_populates="registrations")
    student = relationship("OpStudent")


class OpNotice(Base):
    __tablename__ = "op_notices"
    id = Column(Integer, primary_key=True)
    title = Column(String(256), nullable=False)
    body = Column(Text)
    notice_type = Column(String(32), default="general")
    published_date = Column(Date)
    expiry_date = Column(Date)
    is_pinned = Column(Boolean, default=False)
    active = Column(Boolean, default=True)


class OpBlogPost(Base):
    __tablename__ = "op_blog_posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(256), nullable=False)
    body = Column(Text)
    author_id = Column(Integer, ForeignKey("op_faculty.id"))
    published_date = Column(DateTime)
    is_published = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    author = relationship("OpFaculty")


class OpScholarship(Base):
    __tablename__ = "op_scholarships"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    scholarship_type = Column(String(64))
    amount = Column(Float, default=0)
    criteria = Column(Text)
    active = Column(Boolean, default=True)
    awards = relationship("OpScholarshipAward", back_populates="scholarship")


class OpScholarshipAward(Base):
    __tablename__ = "op_scholarship_awards"
    id = Column(Integer, primary_key=True)
    scholarship_id = Column(Integer, ForeignKey("op_scholarships.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("op_academic_years.id"))
    amount = Column(Float, default=0)
    award_date = Column(Date)
    state = Column(String(16), default="draft")
    scholarship = relationship("OpScholarship", back_populates="awards")
    student = relationship("OpStudent")


class OpAlumni(Base):
    __tablename__ = "op_alumni"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    graduation_year = Column(Integer)
    current_institution = Column(String(256))
    current_employer = Column(String(256))
    email = Column(String(128))
    phone = Column(String(20))
    active = Column(Boolean, default=True)
    student = relationship("OpStudent")


class OpFacility(Base):
    __tablename__ = "op_facilities"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    facility_type = Column(String(64))
    capacity = Column(Integer)
    location = Column(String(256))
    state = Column(String(16), default="available")
    active = Column(Boolean, default=True)
