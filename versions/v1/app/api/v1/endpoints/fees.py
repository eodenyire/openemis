from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.api.crud import get_one, get_all, create_obj, update_obj, delete_obj
from app.models.fees import FeesTerm, FeesTermLine, FeesElement, StudentFeeInvoice, FeePayment
from app.schemas.fees import (
    FeesTermCreate, FeesTermUpdate, FeesTermOut,
    InvoiceCreate, InvoiceUpdate, InvoiceOut,
    PaymentCreate, PaymentOut,
)

router = APIRouter()

# ── Fees Terms ────────────────────────────────────────────────────────────────
@router.get("/terms", response_model=List[FeesTermOut], tags=["Fees"])
def list_fees_terms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, FeesTerm, skip, limit)

@router.post("/terms", response_model=FeesTermOut, status_code=201, tags=["Fees"])
def create_fees_term(data: FeesTermCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    payload = data.model_dump(exclude={"lines"})
    term = create_obj(db, FeesTerm, payload)
    for line_data in (data.lines or []):
        line_payload = {k: v for k, v in line_data.model_dump(exclude={"elements"}).items()}
        line_payload["fees_term_id"] = term.id
        line = create_obj(db, FeesTermLine, line_payload)
        for elem in (line_data.elements or []):
            create_obj(db, FeesElement, {**elem.model_dump(), "fees_term_line_id": line.id})
    db.refresh(term)
    return term

@router.get("/terms/{id}", response_model=FeesTermOut, tags=["Fees"])
def get_fees_term(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, FeesTerm, id)
    if not obj: raise HTTPException(404, "Fees term not found")
    return obj

@router.put("/terms/{id}", response_model=FeesTermOut, tags=["Fees"])
def update_fees_term(id: int, data: FeesTermUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, FeesTerm, id)
    if not obj: raise HTTPException(404, "Fees term not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/terms/{id}", status_code=204, tags=["Fees"])
def delete_fees_term(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, FeesTerm, id)
    if not obj: raise HTTPException(404, "Fees term not found")
    delete_obj(db, obj)


# ── Invoices ──────────────────────────────────────────────────────────────────
@router.get("/invoices", response_model=List[InvoiceOut], tags=["Fees"])
def list_invoices(skip: int = 0, limit: int = 100, student_id: int = None,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(StudentFeeInvoice)
    if student_id: q = q.filter(StudentFeeInvoice.student_id == student_id)
    return q.offset(skip).limit(limit).all()

@router.post("/invoices", response_model=InvoiceOut, status_code=201, tags=["Fees"])
def create_invoice(data: InvoiceCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, StudentFeeInvoice, data.model_dump())

@router.get("/invoices/{id}", response_model=InvoiceOut, tags=["Fees"])
def get_invoice(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, StudentFeeInvoice, id)
    if not obj: raise HTTPException(404, "Invoice not found")
    return obj

@router.put("/invoices/{id}", response_model=InvoiceOut, tags=["Fees"])
def update_invoice(id: int, data: InvoiceUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, StudentFeeInvoice, id)
    if not obj: raise HTTPException(404, "Invoice not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.post("/invoices/{id}/confirm", response_model=InvoiceOut, tags=["Fees"])
def confirm_invoice(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, StudentFeeInvoice, id)
    if not obj: raise HTTPException(404, "Invoice not found")
    return update_obj(db, obj, {"state": "confirmed"})

@router.post("/invoices/{id}/cancel", response_model=InvoiceOut, tags=["Fees"])
def cancel_invoice(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, StudentFeeInvoice, id)
    if not obj: raise HTTPException(404, "Invoice not found")
    return update_obj(db, obj, {"state": "cancelled"})


# ── Payments ──────────────────────────────────────────────────────────────────
@router.get("/payments", response_model=List[PaymentOut], tags=["Fees"])
def list_payments(skip: int = 0, limit: int = 100, invoice_id: int = None,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(FeePayment)
    if invoice_id: q = q.filter(FeePayment.invoice_id == invoice_id)
    return q.offset(skip).limit(limit).all()

@router.post("/payments", response_model=PaymentOut, status_code=201, tags=["Fees"])
def create_payment(data: PaymentCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    invoice = get_one(db, StudentFeeInvoice, data.invoice_id)
    if not invoice: raise HTTPException(404, "Invoice not found")
    payment = create_obj(db, FeePayment, data.model_dump())
    # Update paid amount on invoice
    new_paid = (invoice.paid_amount or 0) + data.amount
    state = "paid" if new_paid >= invoice.total_amount else "partial"
    update_obj(db, invoice, {"paid_amount": new_paid, "state": state})
    return payment

@router.get("/payments/{id}", response_model=PaymentOut, tags=["Fees"])
def get_payment(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, FeePayment, id)
    if not obj: raise HTTPException(404, "Payment not found")
    return obj
