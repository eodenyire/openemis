"""Student lifecycle models — transfers, promotions, alumni."""
import enum
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class TransferType(str, enum.Enum):
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"


class TransferStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class StudentTransfer(Base):
    """Inter-school student transfer with NEMIS UPI tracking."""
    __tablename__ = "student_transfers"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    transfer_type = Column(Enum(TransferType), nullable=False)
    from_school = Column(String(200))
    to_school = Column(String(200))
    nemis_upi = Column(String(50))
    reason = Column(Text)
    transfer_date = Column(Date)
    status = Column(Enum(TransferStatus), default=TransferStatus.PENDING)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    approved_by = relationship("User")


class PromotionBatch(Base):
    """End-of-year bulk promotion record."""
    __tablename__ = "promotion_batches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    from_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    to_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    promoted_count = Column(Integer, default=0)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    academic_year = relationship("AcademicYear")
    from_course = relationship("Course", foreign_keys=[from_course_id])
    to_course = relationship("Course", foreign_keys=[to_course_id])


class Alumni(Base):
    """Graduated students — alumni tracking."""
    __tablename__ = "alumni_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, unique=True)
    graduation_year = Column(Integer, nullable=False)
    final_grade = Column(String(10))
    current_institution = Column(String(200))
    current_employer = Column(String(200))
    career_path = Column(String(200))
    contact_email = Column(String(200))
    contact_phone = Column(String(30))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
