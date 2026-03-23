"""M-Pesa Daraja integration models."""
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class MpesaTransactionStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class MpesaTransaction(Base):
    """Tracks every M-Pesa STK Push transaction."""
    __tablename__ = "mpesa_transactions"

    id = Column(Integer, primary_key=True, index=True)

    # Daraja API fields
    checkout_request_id = Column(String(100), unique=True, nullable=False, index=True)
    merchant_request_id = Column(String(100), nullable=True)

    # Payment details
    phone_number = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)
    account_reference = Column(String(100))   # e.g. invoice number
    transaction_desc = Column(String(200))

    # Status
    status = Column(Enum(MpesaTransactionStatus), default=MpesaTransactionStatus.PENDING)
    result_code = Column(String(10), nullable=True)
    result_desc = Column(Text, nullable=True)

    # Confirmed transaction details (from callback)
    mpesa_receipt_number = Column(String(50), nullable=True, index=True)
    transaction_date = Column(String(20), nullable=True)

    # Links
    invoice_id = Column(Integer, ForeignKey("student_fee_invoices.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)

    # Raw callback payload for audit
    callback_payload = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    invoice = relationship("StudentFeeInvoice")
    student = relationship("Student")
