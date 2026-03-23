"""Fees models — translated from openeducat_fees."""
from datetime import date
from sqlalchemy import Column, Integer, String, Boolean, Date, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class OpFeesTerms(Base):
    __tablename__ = "op_fees_terms"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    code = Column(String(32), unique=True, nullable=False)
    fees_terms = Column(String(16), default="fixed_days")  # fixed_days | fixed_date
    no_days = Column(Integer, default=0)
    day_type = Column(String(8))  # before | after
    discount = Column(Float, default=0)
    note = Column(Text)
    active = Column(Boolean, default=True)
    lines = relationship("OpFeesTermsLine", back_populates="fees_term")


class OpFeesTermsLine(Base):
    __tablename__ = "op_fees_terms_lines"
    id = Column(Integer, primary_key=True)
    fees_term_id = Column(Integer, ForeignKey("op_fees_terms.id"), nullable=False)
    due_days = Column(Integer, default=0)
    due_date = Column(Date)
    value = Column(Float, default=0)  # percentage
    fees_term = relationship("OpFeesTerms", back_populates="lines")
    elements = relationship("OpFeesElement", back_populates="line")


class OpFeesElement(Base):
    __tablename__ = "op_fees_elements"
    id = Column(Integer, primary_key=True)
    line_id = Column(Integer, ForeignKey("op_fees_terms_lines.id"), nullable=False)
    name = Column(String(128), nullable=False)
    value = Column(Float, default=0)
    sequence = Column(Integer, default=1)
    line = relationship("OpFeesTermsLine", back_populates="elements")


class OpStudentFeeInvoice(Base):
    __tablename__ = "op_student_fee_invoices"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("op_courses.id"))
    batch_id = Column(Integer, ForeignKey("op_batches.id"))
    academic_year_id = Column(Integer, ForeignKey("op_academic_years.id"))
    academic_term_id = Column(Integer, ForeignKey("op_academic_terms.id"))
    fees_term_id = Column(Integer, ForeignKey("op_fees_terms.id"))
    total_amount = Column(Float, default=0)
    paid_amount = Column(Float, default=0)
    due_date = Column(Date)
    state = Column(String(16), default="draft")  # draft | confirmed | paid | overdue | cancelled
    note = Column(Text)
    student = relationship("OpStudent")
    course = relationship("OpCourse")
    payments = relationship("OpFeePayment", back_populates="invoice")


class OpFeePayment(Base):
    __tablename__ = "op_fee_payments"
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("op_student_fee_invoices.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(Date)
    payment_method = Column(String(32), default="cash")  # cash | mpesa | bank | cheque
    reference = Column(String(64))
    note = Column(Text)
    invoice = relationship("OpStudentFeeInvoice", back_populates="payments")
