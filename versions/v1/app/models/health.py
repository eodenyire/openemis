"""Health module models — student health records, clinic visits, vaccinations."""
import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    ForeignKey, Float, Text, Enum, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

student_conditions = Table("student_conditions", Base.metadata,
    Column("health_id", Integer, ForeignKey("student_health.id", ondelete="CASCADE")),
    Column("condition_id", Integer, ForeignKey("medical_conditions.id", ondelete="CASCADE")),
)
student_vaccinations = Table("student_vaccinations", Base.metadata,
    Column("health_id", Integer, ForeignKey("student_health.id", ondelete="CASCADE")),
    Column("vaccination_id", Integer, ForeignKey("vaccinations.id", ondelete="CASCADE")),
)


class VisitType(str, enum.Enum):
    ROUTINE    = "routine"
    SICK       = "sick"
    INJURY     = "injury"
    FOLLOW_UP  = "follow_up"
    EMERGENCY  = "emergency"


class VisitDisposition(str, enum.Enum):
    TREATED_SENT_BACK  = "treated_sent_back"
    SENT_HOME          = "sent_home"
    REFERRED_HOSPITAL  = "referred_hospital"
    ADMITTED           = "admitted"


class MedicalCondition(Base):
    __tablename__ = "medical_conditions"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)


class Vaccination(Base):
    __tablename__ = "vaccinations"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    doses_required = Column(Integer, default=1)


class StudentHealth(Base):
    __tablename__ = "student_health"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, unique=True)
    blood_group = Column(String(5))
    height = Column(Float)          # cm
    weight = Column(Float)          # kg
    bmi = Column(Float)             # computed
    allergies = Column(Text)
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relation = Column(String(100))
    doctor_name = Column(String(200))
    doctor_phone = Column(String(20))
    insurance_provider = Column(String(100))
    insurance_number = Column(String(50))
    last_checkup_date = Column(Date)
    notes = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student = relationship("Student")
    conditions = relationship("MedicalCondition", secondary=student_conditions)
    vaccinations = relationship("Vaccination", secondary=student_vaccinations)
    clinic_visits = relationship("ClinicVisit", back_populates="health_record")
    vaccination_records = relationship("VaccinationRecord", back_populates="health_record")


class ClinicVisit(Base):
    """School clinic visit record."""
    __tablename__ = "clinic_visits"

    id = Column(Integer, primary_key=True, index=True)
    health_id = Column(Integer, ForeignKey("student_health.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    visit_date = Column(Date, nullable=False)
    visit_type = Column(Enum(VisitType), default=VisitType.SICK)
    complaint = Column(Text, nullable=False)
    diagnosis = Column(Text)
    treatment = Column(Text)
    medication_given = Column(Text)
    disposition = Column(Enum(VisitDisposition), default=VisitDisposition.TREATED_SENT_BACK)
    referred_to = Column(String(200))       # hospital/specialist name if referred
    follow_up_date = Column(Date)
    attended_by = Column(String(200))       # nurse/doctor name
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    health_record = relationship("StudentHealth", back_populates="clinic_visits")
    student = relationship("Student")


class VaccinationRecord(Base):
    """Record of a vaccination given to a student."""
    __tablename__ = "vaccination_records"

    id = Column(Integer, primary_key=True, index=True)
    health_id = Column(Integer, ForeignKey("student_health.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    vaccination_id = Column(Integer, ForeignKey("vaccinations.id"), nullable=False)
    dose_number = Column(Integer, default=1)
    date_given = Column(Date, nullable=False)
    batch_number = Column(String(50))
    administered_by = Column(String(200))
    next_dose_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    health_record = relationship("StudentHealth", back_populates="vaccination_records")
    student = relationship("Student")
    vaccination = relationship("Vaccination")
