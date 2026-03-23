"""Fees module models"""
import enum
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class PaymentState(str, enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class FeesTerm(Base):
    __tablename__ = "fees_terms"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True)
    note = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lines = relationship("FeesTermLine", back_populates="term", cascade="all, delete-orphan")


class FeesTermLine(Base):
    __tablename__ = "fees_term_lines"
    id = Column(Integer, primary_key=True)
    term_id = Column(Integer, ForeignKey("fees_terms.id"), nullable=False)
    name = Column(String(200), nullable=False)
    due_date = Column(Date)
    due_days = Column(Integer)
    percentage = Column(Float)   # % of total fee
    amount = Column(Float)

    term = relationship("FeesTerm", back_populates="lines")
    elements = relationship("FeesElement", back_populates="term_line", cascade="all, delete-orphan")


class FeesElement(Base):
    __tablename__ = "fees_elements"
    id = Column(Integer, primary_key=True)
    term_line_id = Column(Integer, ForeignKey("fees_term_lines.id"), nullable=False)
    name = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)

    term_line = relationship("FeesTermLine", back_populates="elements")


class StudentFeeInvoice(Base):
    __tablename__ = "student_fee_invoices"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    academic_term_id = Column(Integer, ForeignKey("academic_terms.id"))
    fees_term_id = Column(Integer, ForeignKey("fees_terms.id"))
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0)
    due_date = Column(Date)
    state = Column(Enum(PaymentState), default=PaymentState.PENDING)
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    course = relationship("Course")
    academic_year = relationship("AcademicYear")
    payments = relationship("FeePayment", back_populates="invoice", cascade="all, delete-orphan")


class FeePayment(Base):
    __tablename__ = "fee_payments"
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("student_fee_invoices.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_method = Column(String(50))   # cash, bank, mpesa, etc.
    reference = Column(String(100))
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    invoice = relationship("StudentFeeInvoice", back_populates="payments")
