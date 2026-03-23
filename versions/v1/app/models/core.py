"""
Core academic models: Department, Program, ProgramLevel,
Course, Batch, Subject, AcademicYear, AcademicTerm, StudentCategory
"""
import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    ForeignKey, Float, Text, Enum, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

# ── Association tables ────────────────────────────────────────────────────────

course_subjects = Table(
    "course_subjects", Base.metadata,
    Column("course_id", Integer, ForeignKey("courses.id", ondelete="CASCADE")),
    Column("subject_id", Integer, ForeignKey("subjects.id", ondelete="CASCADE")),
)

teacher_subjects = Table(
    "teacher_subjects", Base.metadata,
    Column("teacher_id", Integer, ForeignKey("teachers.id", ondelete="CASCADE")),
    Column("subject_id", Integer, ForeignKey("subjects.id", ondelete="CASCADE")),
)

student_course_subjects = Table(
    "student_course_subjects", Base.metadata,
    Column("student_course_id", Integer, ForeignKey("student_courses.id", ondelete="CASCADE")),
    Column("subject_id", Integer, ForeignKey("subjects.id", ondelete="CASCADE")),
)

student_parent = Table(
    "student_parent", Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id", ondelete="CASCADE")),
    Column("parent_id", Integer, ForeignKey("parents.id", ondelete="CASCADE")),
)


# ── Enums ─────────────────────────────────────────────────────────────────────

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BloodGroup(str, enum.Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    O_POS = "O+"
    O_NEG = "O-"
    AB_POS = "AB+"
    AB_NEG = "AB-"


class EvaluationType(str, enum.Enum):
    NORMAL = "normal"
    GPA = "GPA"
    CWA = "CWA"
    CCE = "CCE"


class SubjectType(str, enum.Enum):
    THEORY = "theory"
    PRACTICAL = "practical"
    BOTH = "both"
    OTHER = "other"


class SubjectCategory(str, enum.Enum):
    COMPULSORY = "compulsory"
    ELECTIVE = "elective"


# ── Models ────────────────────────────────────────────────────────────────────

class ProgramLevel(Base):
    __tablename__ = "program_levels"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), unique=True)
    description = Column(Text)
    active = Column(Boolean, default=True)
    programs = relationship("Program", back_populates="program_level")


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True, index=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("departments.id"))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent = relationship("Department", remote_side=[id], backref="children")
    courses = relationship("Course", back_populates="department")
    programs = relationship("Program", back_populates="department")
    subjects = relationship("Subject", back_populates="department")
    faculty = relationship("Teacher", back_populates="main_department",
                           foreign_keys="Teacher.main_department_id")


class Program(Base):
    __tablename__ = "programs"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True, index=True, nullable=False)
    description = Column(Text)
    max_unit_load = Column(Float)
    min_unit_load = Column(Float)
    department_id = Column(Integer, ForeignKey("departments.id"))
    program_level_id = Column(Integer, ForeignKey("program_levels.id"))
    image = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    department = relationship("Department", back_populates="programs")
    program_level = relationship("ProgramLevel", back_populates="programs")
    courses = relationship("Course", back_populates="program")


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("courses.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    program_id = Column(Integer, ForeignKey("programs.id"))
    evaluation_type = Column(Enum(EvaluationType), default=EvaluationType.NORMAL)
    max_unit_load = Column(Float)
    min_unit_load = Column(Float)
    duration_years = Column(Integer)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent = relationship("Course", remote_side=[id], backref="children")
    department = relationship("Department", back_populates="courses")
    program = relationship("Program", back_populates="courses")
    subjects = relationship("Subject", secondary=course_subjects, back_populates="courses")
    batches = relationship("Batch", back_populates="course")
    enrollments = relationship("StudentCourse", back_populates="course")


class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True, index=True, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course", back_populates="batches")
    enrollments = relationship("StudentCourse", back_populates="batch")


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    credits = Column(Integer)
    grade_weightage = Column(Float)
    type = Column(Enum(SubjectType), default=SubjectType.THEORY)
    subject_type = Column(Enum(SubjectCategory), default=SubjectCategory.COMPULSORY)
    department_id = Column(Integer, ForeignKey("departments.id"))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    department = relationship("Department", back_populates="subjects")
    courses = relationship("Course", secondary=course_subjects, back_populates="subjects")
    teachers = relationship("Teacher", secondary=teacher_subjects, back_populates="subjects")


class AcademicYear(Base):
    __tablename__ = "academic_years"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, index=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False)
    active = Column(Boolean, default=True)

    terms = relationship("AcademicTerm", back_populates="academic_year")


class AcademicTerm(Base):
    __tablename__ = "academic_terms"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, index=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    active = Column(Boolean, default=True)

    academic_year = relationship("AcademicYear", back_populates="terms")


class StudentCategory(Base):
    __tablename__ = "student_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), unique=True)
    description = Column(Text)
    active = Column(Boolean, default=True)

    students = relationship("Student", back_populates="category")
