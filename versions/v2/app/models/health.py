"""Health models — translated from openemis_health."""
from datetime import date
from sqlalchemy import Column, Integer, String, Boolean, Date, Float, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.base import Base


# ── Association tables ────────────────────────────────────────────────────────

student_health_condition_rel = Table(
    "op_student_health_condition_rel", Base.metadata,
    Column("health_id", Integer, ForeignKey("op_student_health.id"), primary_key=True),
    Column("condition_id", Integer, ForeignKey("op_medical_conditions.id"), primary_key=True),
)

student_health_vaccination_rel = Table(
    "op_student_health_vaccination_rel", Base.metadata,
    Column("health_id", Integer, ForeignKey("op_student_health.id"), primary_key=True),
    Column("vaccination_id", Integer, ForeignKey("op_vaccinations.id"), primary_key=True),
)


# ── Lookup tables ─────────────────────────────────────────────────────────────

class OpMedicalCondition(Base):
    __tablename__ = "op_medical_conditions"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(Text)
    active = Column(Boolean, default=True)


class OpVaccination(Base):
    __tablename__ = "op_vaccinations"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(Text)
    active = Column(Boolean, default=True)


# ── Student Health Record ─────────────────────────────────────────────────────

class OpStudentHealth(Base):
    __tablename__ = "op_student_health"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    blood_group = Column(String(4))  # A+, B+, O+, AB+, A-, B-, O-, AB-
    height = Column(Float)           # cm
    weight = Column(Float)           # kg
    bmi = Column(Float, default=0.0)
    allergies = Column(Text)
    emergency_contact_name = Column(String(128))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relation = Column(String(64))
    doctor_name = Column(String(128))
    doctor_phone = Column(String(20))
    notes = Column(Text)
    last_checkup_date = Column(Date)
    active = Column(Boolean, default=True)
    student = relationship("OpStudent")
    medical_conditions = relationship("OpMedicalCondition", secondary=student_health_condition_rel)
    vaccinations = relationship("OpVaccination", secondary=student_health_vaccination_rel)
