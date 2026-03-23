"""DigiGuide models — academic performance, national exam prediction, KUCCPS careers."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Float, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.cbc import prediction_performance_rel


class OpAcademicPerformance(Base):
    __tablename__ = "op_academic_performances"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("op_subjects.id"), nullable=False)
    academic_year = Column(String(16), nullable=False)
    grade = Column(String(16), nullable=False)  # grade_1 .. grade_12
    term = Column(String(8), nullable=False)    # term_1, term_2, term_3
    assessment_type = Column(String(32), nullable=False)  # weekly_assignment, mid_term, termly, annual
    score = Column(Float, nullable=False)
    max_score = Column(Float, default=100.0)
    percentage = Column(Float, default=0.0)
    grade_letter = Column(String(4))
    notes = Column(Text)
    is_national_exam_grade = Column(Boolean, default=False)
    student = relationship("OpStudent")
    subject = relationship("OpSubject")


class OpNationalExamPrediction(Base):
    __tablename__ = "op_national_exam_predictions"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    national_exam_grade = Column(String(16), nullable=False)  # grade_3, grade_6, grade_9, grade_12
    predicted_percentage = Column(Float, default=0.0)
    predicted_grade_letter = Column(String(4))
    confidence_level = Column(Float, default=0.0)
    computation_date = Column(DateTime, default=datetime.utcnow)
    state = Column(String(16), default="draft")  # draft, computed, confirmed
    notes = Column(Text)
    student = relationship("OpStudent")
    performance_records = relationship(
        "OpAcademicPerformance",
        secondary=prediction_performance_rel,
    )


class OpKuccpsCareer(Base):
    __tablename__ = "op_kuccps_careers"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    kuccps_code = Column(String(32), unique=True)
    cluster = Column(String(128))
    minimum_grade = Column(String(8))
    minimum_points = Column(Float, default=0.0)
    required_subjects = Column(Text)
    institution_name = Column(String(256))
    institution_type = Column(String(16))  # university, college
    duration_years = Column(Float, default=0.0)
    description = Column(Text)
    sync_status = Column(String(16), default="pending")  # pending, synced, error
    last_sync_date = Column(DateTime)
    raw_api_response = Column(Text)
    active = Column(Boolean, default=True)


class OpCareerMatch(Base):
    __tablename__ = "op_career_matches_v2"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    career_id = Column(Integer, ForeignKey("op_kuccps_careers.id"), nullable=False)
    prediction_id = Column(Integer, ForeignKey("op_national_exam_predictions.id"))
    predicted_percentage = Column(Float, default=0.0)
    minimum_points = Column(Float, default=0.0)
    match_status = Column(String(32), default="not_evaluated")  # not_evaluated, eligible, conditionally_eligible, not_eligible
    match_score = Column(Float, default=0.0)
    evaluation_date = Column(DateTime)
    counsellor_notes = Column(Text)
    student = relationship("OpStudent")
    career = relationship("OpKuccpsCareer")
    prediction = relationship("OpNationalExamPrediction")
