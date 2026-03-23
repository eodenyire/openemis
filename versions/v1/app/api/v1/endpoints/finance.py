"""Finance endpoints — bulk invoicing, reconciliation, reports."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date, timedelta
from app.db.session import get_db
from app.api.deps import require_admin, get_current_user
from app.models.fees import StudentFeeInvoice, FeePayment, FeesTerm, PaymentState
from app.models.people import StudentCourse

router = APIRouter()


class BulkInvoiceRequest(BaseModel):
    academic_year_id: int
    academic_term_id: int
    fees_term_id: int
    total_amount: float
    due_days: int = 30
    course_ids: Optional[list[int]] = None


@router.post("/invoices/bulk-generate")
def bulk_generate_invoices(
    payload: BulkInvoiceRequest,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Generate fee invoices for all enrolled students (or specific courses)."""
    query = db.query(StudentCourse).filter(
        StudentCourse.academic_year_id == payload.academic_year_id,
        StudentCourse.state == "running",
    )
    if payload.course_ids:
        query = query.filter(StudentCourse.course_id.in_(payload.course_ids))

    enrollments = query.all()
    due_date = date.today() + timedelta(days=payload.due_days)
    created = 0
    skipped = 0

    for sc in enrollments:
        existing = db.query(StudentFeeInvoice).filter(
            StudentFeeInvoice.student_id == sc.student_id,
            StudentFeeInvoice.academic_term_id == payload.academic_term_id,
            StudentFeeInvoice.fees_term_id == payload.fees_term_id,
        ).first()
        if existing:
            skipped += 1
            continue
        invoice = StudentFeeInvoice(
            student_id=sc.student_id,
            course_id=sc.course_id,
            academic_year_id=payload.academic_year_id,
            academic_term_id=payload.academic_term_id,
            fees_term_id=payload.fees_term_id,
            total_amount=payload.total_amount,
            paid_amount=0.0,
            due_date=due_date,
            state=PaymentState.PENDING,
        )
        db.add(invoice)
        created += 1

    db.commit()
    return {"created": created, "skipped": skipped}


@router.get("/summary")
def finance_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_invoiced = db.query(func.coalesce(func.sum(StudentFeeInvoice.total_amount), 0)).scalar()
    total_paid = db.query(func.coalesce(func.sum(FeePayment.amount), 0)).scalar()
    total_invoices = db.query(func.count(StudentFeeInvoice.id)).scalar()
    paid_invoices = db.query(func.count(StudentFeeInvoice.id)).filter(
        StudentFeeInvoice.state == PaymentState.PAID
    ).scalar()
    overdue = db.query(func.count(StudentFeeInvoice.id)).filter(
        StudentFeeInvoice.state == PaymentState.PENDING,
        StudentFeeInvoice.due_date < date.today(),
    ).scalar()

    # Payment method breakdown
    methods = db.query(
        FeePayment.payment_method,
        func.count(FeePayment.id).label("count"),
        func.sum(FeePayment.amount).label("total"),
    ).group_by(FeePayment.payment_method).all()

    return {
        "total_invoiced_kes": float(total_invoiced),
        "total_collected_kes": float(total_paid),
        "outstanding_kes": float(total_invoiced) - float(total_paid),
        "collection_rate_pct": round(float(total_paid) / float(total_invoiced) * 100, 1) if total_invoiced else 0,
        "total_invoices": total_invoices,
        "paid_invoices": paid_invoices,
        "overdue_invoices": overdue,
        "payment_methods": [
            {"method": m.payment_method, "count": m.count, "total_kes": float(m.total or 0)}
            for m in methods
        ],
    }


@router.get("/invoices/overdue")
def overdue_invoices(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
    limit: int = 100,
):
    invoices = db.query(StudentFeeInvoice).filter(
        StudentFeeInvoice.state == PaymentState.PENDING,
        StudentFeeInvoice.due_date < date.today(),
    ).limit(limit).all()
    return invoices
