"""Fees endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.fees import OpFeesTerms, OpFeesElement, OpStudentFeeInvoice, OpFeePayment, OpFeesTermsLine

router = APIRouter()


@router.get("/fees-terms")
def list_fees_terms(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpFeesTerms).filter_by(active=True).all()

@router.post("/fees-terms", status_code=201)
def create_fees_terms(name: str, code: str,
                      db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpFeesTerms(name=name, code=code)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/fees-terms/{id}")
def get_fees_terms(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpFeesTerms).get(id)
    if not obj: raise HTTPException(404, "Fees terms not found")
    return obj


@router.get("/fees-elements")
def list_fees_elements(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpFeesElement).all()

@router.post("/fees-elements", status_code=201)
def create_fees_element(line_id: int, name: str, value: float = 0, sequence: int = 1,
                        db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpFeesElement(line_id=line_id, name=name, value=value, sequence=sequence)
    db.add(obj); db.commit(); db.refresh(obj); return obj


@router.get("/invoices")
def list_invoices(student_id: Optional[int] = None, state: Optional[str] = None,
                  skip: int = 0, limit: int = 100,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpStudentFeeInvoice)
    if student_id: q = q.filter_by(student_id=student_id)
    if state: q = q.filter_by(state=state)
    return {"total": q.count(), "items": q.offset(skip).limit(limit).all()}

@router.post("/invoices", status_code=201)
def create_invoice(student_id: int, fees_term_id: int, due_date: Optional[date] = None,
                   course_id: Optional[int] = None, academic_year_id: Optional[int] = None,
                   db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpStudentFeeInvoice(student_id=student_id, fees_term_id=fees_term_id, due_date=due_date,
                               course_id=course_id, academic_year_id=academic_year_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/invoices/{id}")
def get_invoice(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpStudentFeeInvoice).get(id)
    if not obj: raise HTTPException(404, "Invoice not found")
    return obj


@router.get("/payments")
def list_payments(student_id: Optional[int] = None, invoice_id: Optional[int] = None,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpFeePayment)
    if student_id: q = q.filter_by(student_id=student_id)
    if invoice_id: q = q.filter_by(invoice_id=invoice_id)
    return q.all()

@router.post("/payments", status_code=201)
def create_payment(invoice_id: int, amount: float,
                   payment_date: Optional[date] = None, payment_method: str = "cash",
                   reference: Optional[str] = None,
                   db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpFeePayment(invoice_id=invoice_id, amount=amount,
                       payment_date=payment_date, payment_method=payment_method, reference=reference)
    db.add(obj); db.commit(); db.refresh(obj); return obj
