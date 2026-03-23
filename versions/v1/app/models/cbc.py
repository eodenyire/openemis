"""CBC Curriculum Models — Learning Areas, Strands, Sub-Strands, Competency Indicators."""
import enum
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Enum, Text, Date
from sqlalchemy.orm import relationship
from app.db.base import Base


class GradeBand(str, enum.Enum):
    PRE_PRIMARY = "Pre-Primary"
    LOWER_PRIMARY = "Lower Primary"
    UPPER_PRIMARY = "Upper Primary"
    JUNIOR_SECONDARY = "Junior Secondary"
    SENIOR_SECONDARY = "Senior Secondary"


class PerformanceLevel(str, enum.Enum):
    EE = "EE"   # Exceeds Expectation
    ME = "ME"   # Meets Expectation
    AE = "AE"   # Approaches Expectation
    BE = "BE"   # Below Expectation


class CBCCompetency(str, enum.Enum):
    COMMUNICATION = "Communication and Collaboration"
    CRITICAL_THINKING = "Critical Thinking and Problem Solving"
    CREATIVITY = "Creativity and Imagination"
    CITIZENSHIP = "Citizenship"
    DIGITAL_LITERACY = "Digital Literacy"
    LEARNING_TO_LEARN = "Learning to Learn"
    SELF_EFFICACY = "Self-Efficacy"
    SOCIAL_COHESION = "Social Cohesion and Responsibility"


class CBCGradeLevel(Base):
    """PP1, PP2, Grade 1 … Grade 12 — the 14 CBC grade levels."""
    __tablename__ = "cbc_grade_levels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, nullable=False)   # e.g. "Grade 7"
    code = Column(String(10), unique=True, nullable=False)   # e.g. "G7"
    grade_band = Column(Enum(GradeBand), nullable=False)
    order = Column(Integer, nullable=False)                  # 1=PP1 … 14=Grade12
    is_active = Column(Boolean, default=True)

    learning_areas = relationship("LearningArea", back_populates="grade_level")


class LearningArea(Base):
    """A CBC subject offered at a specific grade level."""
    __tablename__ = "learning_areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)
    grade_level_id = Column(Integer, ForeignKey("cbc_grade_levels.id"), nullable=False)
    is_core = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    grade_level = relationship("CBCGradeLevel", back_populates="learning_areas")
    strands = relationship("Strand", back_populates="learning_area")


class Strand(Base):
    """Thematic grouping within a LearningArea."""
    __tablename__ = "strands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    learning_area_id = Column(Integer, ForeignKey("learning_areas.id"), nullable=False)
    order = Column(Integer, default=1)

    learning_area = relationship("LearningArea", back_populates="strands")
    sub_strands = relationship("SubStrand", back_populates="strand")


class SubStrand(Base):
    """Specific topic within a Strand."""
    __tablename__ = "sub_strands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    strand_id = Column(Integer, ForeignKey("strands.id"), nullable=False)
    order = Column(Integer, default=1)

    strand = relationship("Strand", back_populates="sub_strands")
    competency_indicators = relationship("CompetencyIndicator", back_populates="sub_strand")


class CompetencyIndicator(Base):
    """Measurable learning outcome mapped to a CBC core competency."""
    __tablename__ = "competency_indicators"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    sub_strand_id = Column(Integer, ForeignKey("sub_strands.id"), nullable=False)
    competency = Column(Enum(CBCCompetency), nullable=True)
    order = Column(Integer, default=1)

    sub_strand = relationship("SubStrand", back_populates="competency_indicators")
    scores = relationship("CompetencyScore", back_populates="indicator")


# ── Assessment Models ──────────────────────────────────────────────────────────

class CBCAssessment(Base):
    """A formative or summative assessment event."""
    __tablename__ = "cbc_assessments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    assessment_type = Column(String(30), default="formative")  # formative / summative / CAT
    learning_area_id = Column(Integer, ForeignKey("learning_areas.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    assessment_date = Column(Date, nullable=True)
    term = Column(String(20), nullable=True)
    academic_year = Column(String(10), nullable=True)
    notes = Column(Text, nullable=True)

    learning_area = relationship("LearningArea")
    scores = relationship("CompetencyScore", back_populates="assessment")


class CompetencyScore(Base):
    """A student's performance level on a specific competency indicator."""
    __tablename__ = "competency_scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("cbc_assessments.id"), nullable=False)
    indicator_id = Column(Integer, ForeignKey("competency_indicators.id"), nullable=False)
    performance_level = Column(Enum(PerformanceLevel), nullable=False)
    raw_score = Column(Float, nullable=True)
    teacher_remarks = Column(Text, nullable=True)

    assessment = relationship("CBCAssessment", back_populates="scores")
    indicator = relationship("CompetencyIndicator", back_populates="scores")


class ReportCard(Base):
    """Per-student, per-term CBC report card."""
    __tablename__ = "report_cards"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    grade_level_id = Column(Integer, ForeignKey("cbc_grade_levels.id"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    academic_term_id = Column(Integer, ForeignKey("academic_terms.id"), nullable=False)
    class_teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    principal_remarks = Column(Text, nullable=True)
    teacher_remarks = Column(Text, nullable=True)
    days_present = Column(Integer, default=0)
    days_absent = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)

    lines = relationship("ReportCardLine", back_populates="report_card")


class ReportCardLine(Base):
    """One line per LearningArea on a ReportCard."""
    __tablename__ = "report_card_lines"

    id = Column(Integer, primary_key=True, index=True)
    report_card_id = Column(Integer, ForeignKey("report_cards.id"), nullable=False)
    learning_area_id = Column(Integer, ForeignKey("learning_areas.id"), nullable=False)
    performance_level = Column(Enum(PerformanceLevel), nullable=False)
    teacher_comment = Column(Text, nullable=True)

    report_card = relationship("ReportCard", back_populates="lines")
    learning_area = relationship("LearningArea")
