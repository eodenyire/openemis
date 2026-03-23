"""CBC (Competency-Based Curriculum) models — translated from openemis_cbc."""
from datetime import date
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Float, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.base import Base


# ── Association tables ────────────────────────────────────────────────────────

mentor_group_rel = Table(
    "op_mentor_group_rel", Base.metadata,
    Column("group_id", Integer, ForeignKey("op_mentorship_groups.id"), primary_key=True),
    Column("mentor_id", Integer, ForeignKey("op_mentors.id"), primary_key=True),
)

portfolio_attachment_rel = Table(
    "cbc_portfolio_attachment_rel", Base.metadata,
    Column("portfolio_id", Integer, ForeignKey("cbc_portfolios.id"), primary_key=True),
    Column("attachment_id", Integer, ForeignKey("ir_attachments.id"), primary_key=True),
)

prediction_performance_rel = Table(
    "op_prediction_performance_rel", Base.metadata,
    Column("prediction_id", Integer, ForeignKey("op_national_exam_predictions.id"), primary_key=True),
    Column("performance_id", Integer, ForeignKey("op_academic_performances.id"), primary_key=True),
)


# ── CBC Curriculum Hierarchy ──────────────────────────────────────────────────

class CbcStrand(Base):
    __tablename__ = "cbc_strands"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    code = Column(String(10))
    sequence = Column(Integer, default=10)
    active = Column(Boolean, default=True)
    description = Column(Text)
    grade_band = Column(String(8), default="all")  # lp, up, js, ss, all
    subject_id = Column(Integer, ForeignKey("op_subjects.id"))
    subject = relationship("OpSubject")
    substrands = relationship("CbcSubstrand", back_populates="strand")


class CbcSubstrand(Base):
    __tablename__ = "cbc_substrands"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    code = Column(String(20))
    sequence = Column(Integer, default=10)
    active = Column(Boolean, default=True)
    strand_id = Column(Integer, ForeignKey("cbc_strands.id"), nullable=False)
    description = Column(Text)
    strand = relationship("CbcStrand", back_populates="substrands")
    outcomes = relationship("CbcLearningOutcome", back_populates="substrand")


class CbcLearningOutcome(Base):
    __tablename__ = "cbc_learning_outcomes"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    code = Column(String(30))
    sequence = Column(Integer, default=10)
    active = Column(Boolean, default=True)
    substrand_id = Column(Integer, ForeignKey("cbc_substrands.id"), nullable=False)
    grade_level = Column(String(4), nullable=False)  # pp1, pp2, g1..g12
    description = Column(Text)
    substrand = relationship("CbcSubstrand", back_populates="outcomes")
    rubrics = relationship("CbcRubric", back_populates="outcome")


class CbcRubric(Base):
    __tablename__ = "cbc_rubrics"
    id = Column(Integer, primary_key=True)
    outcome_id = Column(Integer, ForeignKey("cbc_learning_outcomes.id"), nullable=False)
    level = Column(String(4), nullable=False)  # em, me, ap, be
    level_code = Column(String(4))
    descriptor = Column(Text, nullable=False)
    score = Column(Float, default=0.0)
    outcome = relationship("CbcLearningOutcome", back_populates="rubrics")


# ── CBC Assessments & Portfolios ──────────────────────────────────────────────

class IrAttachment(Base):
    """Minimal stub for file attachments."""
    __tablename__ = "ir_attachments"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    file_path = Column(String(512))
    mimetype = Column(String(64))


class CbcPortfolio(Base):
    __tablename__ = "cbc_portfolios"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    grade_level = Column(String(4), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("op_academic_years.id"))
    term = Column(String(8), default="annual")  # term1, term2, term3, annual
    description = Column(Text)
    teacher_comment = Column(Text)
    parent_comment = Column(Text)
    state = Column(String(16), default="draft")  # draft, submitted, reviewed
    student = relationship("OpStudent")
    assessments = relationship("CbcFormativeAssessment", back_populates="portfolio")
    attachments = relationship("IrAttachment", secondary=portfolio_attachment_rel)


class CbcFormativeAssessment(Base):
    __tablename__ = "cbc_formative_assessments"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    date = Column(Date, nullable=False)
    assessment_type = Column(String(16), nullable=False)  # observation, oral, written, project, portfolio, peer
    grade_level = Column(String(4), nullable=False)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("op_faculty.id"))
    subject_id = Column(Integer, ForeignKey("op_subjects.id"))
    outcome_id = Column(Integer, ForeignKey("cbc_learning_outcomes.id"))
    performance_level = Column(String(4), nullable=False)  # em, me, ap, be
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=4.0)
    observations = Column(Text)
    term = Column(String(8), nullable=False, default="term1")
    academic_year_id = Column(Integer, ForeignKey("op_academic_years.id"))
    portfolio_id = Column(Integer, ForeignKey("cbc_portfolios.id"))
    state = Column(String(16), default="draft")  # draft, confirmed, approved
    student = relationship("OpStudent")
    teacher = relationship("OpFaculty")
    portfolio = relationship("CbcPortfolio", back_populates="assessments")


# ── CBC Report Cards ──────────────────────────────────────────────────────────

class CbcReportCard(Base):
    __tablename__ = "cbc_report_cards"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    grade_level = Column(String(4), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("op_academic_years.id"), nullable=False)
    term = Column(String(8), nullable=False, default="term1")
    teacher_id = Column(Integer, ForeignKey("op_faculty.id"))
    class_teacher_comment = Column(Text)
    principal_comment = Column(Text)
    parent_comment = Column(Text)
    state = Column(String(16), default="draft")  # draft, published, acknowledged
    total_score = Column(Float, default=0.0)
    average_score = Column(Float, default=0.0)
    student = relationship("OpStudent")
    lines = relationship("CbcReportCardLine", back_populates="report_card")


class CbcReportCardLine(Base):
    __tablename__ = "cbc_report_card_lines"
    id = Column(Integer, primary_key=True)
    report_card_id = Column(Integer, ForeignKey("cbc_report_cards.id"), nullable=False)
    strand_id = Column(Integer, ForeignKey("cbc_strands.id"), nullable=False)
    outcome_id = Column(Integer, ForeignKey("cbc_learning_outcomes.id"))
    performance_level = Column(String(4))  # em, me, ap, be
    score = Column(Float, default=0.0)
    teacher_remark = Column(Text)
    report_card = relationship("CbcReportCard", back_populates="lines")
