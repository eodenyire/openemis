"""Core models — translated from openeducat_core."""
from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    Float, Text, ForeignKey, Table, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class EvaluationType(str, enum.Enum):
    normal = "normal"
    GPA = "GPA"
    CWA = "CWA"
    CCE = "CCE"


class SubjectType(str, enum.Enum):
    theory = "theory"
    practical = "practical"
    both = "both"


# ── Association tables ────────────────────────────────────────────────────────

course_subject = Table(
    "op_course_subject", Base.metadata,
    Column("course_id", Integer, ForeignKey("op_courses.id"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("op_subjects.id"), primary_key=True),
)

faculty_subject = Table(
    "op_faculty_subject", Base.metadata,
    Column("faculty_id", Integer, ForeignKey("op_faculty.id"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("op_subjects.id"), primary_key=True),
)

student_course_subject = Table(
    "op_student_course_subject", Base.metadata,
    Column("student_course_id", Integer, ForeignKey("op_student_courses.id"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("op_subjects.id"), primary_key=True),
)


# ── Models ────────────────────────────────────────────────────────────────────

class OpDepartment(Base):
    __tablename__ = "op_departments"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    code = Column(String(16), unique=True)
    active = Column(Boolean, default=True)


class OpProgram(Base):
    __tablename__ = "op_programs"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    code = Column(String(16), unique=True)
    active = Column(Boolean, default=True)


class OpAcademicYear(Base):
    __tablename__ = "op_academic_years"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    active = Column(Boolean, default=True)


class OpAcademicTerm(Base):
    __tablename__ = "op_academic_terms"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("op_academic_years.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    active = Column(Boolean, default=True)
    academic_year = relationship("OpAcademicYear")


class OpCourse(Base):
    __tablename__ = "op_courses"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    code = Column(String(16), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("op_courses.id"), nullable=True)
    evaluation_type = Column(SAEnum(EvaluationType), default=EvaluationType.normal)
    department_id = Column(Integer, ForeignKey("op_departments.id"))
    program_id = Column(Integer, ForeignKey("op_programs.id"))
    max_unit_load = Column(Float, default=0)
    min_unit_load = Column(Float, default=0)
    active = Column(Boolean, default=True)
    subjects = relationship("OpSubject", secondary=course_subject, back_populates="courses")
    department = relationship("OpDepartment")


class OpSubject(Base):
    __tablename__ = "op_subjects"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    code = Column(String(16), unique=True, nullable=False)
    grade_weightage = Column(Float, default=0)
    subject_type = Column(String(32), default="theory")
    elective_or_compulsory = Column(String(16), default="compulsory")
    department_id = Column(Integer, ForeignKey("op_departments.id"))
    active = Column(Boolean, default=True)
    courses = relationship("OpCourse", secondary=course_subject, back_populates="subjects")


class OpBatch(Base):
    __tablename__ = "op_batches"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    code = Column(String(16))
    course_id = Column(Integer, ForeignKey("op_courses.id"), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    active = Column(Boolean, default=True)
    course = relationship("OpCourse")


class OpCategory(Base):
    __tablename__ = "op_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    active = Column(Boolean, default=True)


class OpStudent(Base):
    __tablename__ = "op_students"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    middle_name = Column(String(64))
    last_name = Column(String(64), nullable=False)
    birth_date = Column(Date)
    gender = Column(SAEnum(GenderEnum))
    blood_group = Column(String(8))
    nationality = Column(String(64))
    id_number = Column(String(32))
    gr_no = Column(String(32), unique=True)
    phone = Column(String(20))
    mobile = Column(String(20))
    email = Column(String(128))
    street = Column(String(256))
    city = Column(String(64))
    category_id = Column(Integer, ForeignKey("op_categories.id"))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    category = relationship("OpCategory")
    courses = relationship("OpStudentCourse", back_populates="student")


class OpFaculty(Base):
    __tablename__ = "op_faculty"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    middle_name = Column(String(64))
    last_name = Column(String(64), nullable=False)
    birth_date = Column(Date)
    gender = Column(SAEnum(GenderEnum))
    nationality = Column(String(64))
    emp_id = Column(String(32), unique=True)
    phone = Column(String(20))
    mobile = Column(String(20))
    email = Column(String(128))
    main_department_id = Column(Integer, ForeignKey("op_departments.id"))
    active = Column(Boolean, default=True)
    subjects = relationship("OpSubject", secondary=faculty_subject)
    department = relationship("OpDepartment")


class OpStudentCourse(Base):
    __tablename__ = "op_student_courses"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("op_courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("op_batches.id"))
    roll_number = Column(String(32))
    academic_year_id = Column(Integer, ForeignKey("op_academic_years.id"))
    academic_term_id = Column(Integer, ForeignKey("op_academic_terms.id"))
    state = Column(String(16), default="running")
    student = relationship("OpStudent", back_populates="courses")
    course = relationship("OpCourse")
    batch = relationship("OpBatch")
    subjects = relationship("OpSubject", secondary=student_course_subject)
