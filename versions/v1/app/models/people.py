"""
People models: Teacher, Student, StudentCourse, Parent
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.core import (
    Gender, BloodGroup,
    teacher_subjects, student_course_subjects, student_parent
)


class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    last_name = Column(String(100), nullable=False)
    gender = Column(Enum(Gender))
    date_of_birth = Column(Date)
    blood_group = Column(Enum(BloodGroup))
    nationality = Column(String(100))
    phone = Column(String(20))
    mobile = Column(String(20))
    email = Column(String(200))
    address = Column(Text)
    qualification = Column(String(200))
    specialization = Column(String(200))
    experience_years = Column(Integer)
    join_date = Column(Date)
    main_department_id = Column(Integer, ForeignKey("departments.id"))
    image = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="teacher_profile")
    main_department = relationship("Department", back_populates="faculty",
                                   foreign_keys=[main_department_id])
    subjects = relationship("Subject", secondary=teacher_subjects, back_populates="teachers")


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    admission_number = Column(String(50), unique=True, index=True, nullable=False)
    gr_no = Column(String(50), unique=True, index=True)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    last_name = Column(String(100), nullable=False)
    gender = Column(Enum(Gender))
    date_of_birth = Column(Date)
    blood_group = Column(Enum(BloodGroup))
    nationality = Column(String(100))
    phone = Column(String(20))
    mobile = Column(String(20))
    email = Column(String(200))
    street = Column(String(255))
    street2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relation = Column(String(100))
    id_number = Column(String(100))
    nemis_upi = Column(String(50), nullable=True, index=True)  # NEMIS Unique Pupil Identifier
    category_id = Column(Integer, ForeignKey("student_categories.id"))
    admission_date = Column(Date)
    image = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="student_profile")
    category = relationship("StudentCategory", back_populates="students")
    enrollments = relationship("StudentCourse", back_populates="student",
                               cascade="all, delete-orphan")
    parents = relationship("Parent", secondary=student_parent, back_populates="students")


class StudentCourse(Base):
    """Student enrollment in a course/batch"""
    __tablename__ = "student_courses"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    roll_number = Column(String(50))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    academic_term_id = Column(Integer, ForeignKey("academic_terms.id"))
    state = Column(String(20), default="running")   # running | finished
    fees_start_date = Column(Date)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    batch = relationship("Batch", back_populates="enrollments")
    academic_year = relationship("AcademicYear")
    academic_term = relationship("AcademicTerm")
    subjects = relationship("Subject", secondary=student_course_subjects)


class ParentRelationship(Base):
    __tablename__ = "parent_relationships"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)   # Mother, Father, Guardian…


class Parent(Base):
    __tablename__ = "parents"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200))
    mobile = Column(String(20))
    phone = Column(String(20))
    relationship_id = Column(Integer, ForeignKey("parent_relationships.id"))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="parent_profile")
    relationship_type = relationship("ParentRelationship")
    students = relationship("Student", secondary=student_parent, back_populates="parents")
