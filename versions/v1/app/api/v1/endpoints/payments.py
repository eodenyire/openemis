"""M-Pesa STK Push payment endpoints."""
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.mpesa import MpesaTransaction, MpesaTransactionStatus
from app.models.fees import StudentFeeInvoice, FeePayment, PaymentState
from app.services.mpesa import initiate_stk_push
from app.core.config import settings
from datetime import date

router = APIRouter()


class STKPushRequest(BaseModel):
    phone_number: str
    amount: float
    invoice_id: int
    account_reference: str = ""
    transaction_desc: str = "School Fee Payment"


@router.post("/mpesa/initiate")
async def mpesa_initiate(
    payload: STKPushRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    invoice = db.query(StudentFeeInvoice).filter(
        StudentFeeInvoice.id == payload.invoice_id
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    ref = payload.account_reference or f"INV{payload.invoice_id}"
    callback_url = settings.MPESA_CALLBACK_URL

    try:
        result = await initiate_stk_push(
            phone=payload.phone_number,
            amount=payload.amount,
            account_reference=ref,
            transaction_desc=payload.transaction_desc,
            callback_url=callback_url,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"M-Pesa error: {str(e)}")

    txn = MpesaTransaction(
        checkout_request_id=result.get("CheckoutRequestID", ""),
        merchant_request_id=result.get("MerchantRequestID", ""),
        phone_number=payload.phone_number,
        amount=payload.amount,
        account_reference=ref,
        transaction_desc=payload.transaction_desc,
        invoice_id=payload.invoice_id,
        student_id=invoice.student_id,
        status=MpesaTransactionStatus.PENDING,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    return {
        "message": "STK Push sent. Check your phone.",
        "checkout_request_id": txn.checkout_request_id,
        "transaction_id": txn.id,
    }


@router.post("/mpesa/callback")
async def mpesa_callback(request: Request, db: Session = Depends(get_db)):
    """Safaricom calls this URL after payment attempt."""
    body = await request.json()
    raw = json.dumps(body)

    try:
        stk = body["Body"]["stkCallback"]
        checkout_id = stk["CheckoutRequestID"]
        result_code = str(stk["ResultCode"])
        result_desc = stk.get("ResultDesc", "")
    except (KeyError, TypeError):
        return {"ResultCode": 0, "ResultDesc": "Accepted"}

    txn = db.query(MpesaTransaction).filter(
        MpesaTransaction.checkout_request_id == checkout_id
    ).first()

    if not txn:
        return {"ResultCode": 0, "ResultDesc": "Accepted"}

    # Idempotency — already processed
    if txn.status != MpesaTransactionStatus.PENDING:
        return {"ResultCode": 0, "ResultDesc": "Already processed"}

    txn.result_code = result_code
    txn.result_desc = result_desc
    txn.callback_payload = raw

    if result_code == "0":
        # Extract metadata
        items = {
            i["Name"]: i.get("Value")
            for i in stk.get("CallbackMetadata", {}).get("Item", [])
        }
        txn.mpesa_receipt_number = str(items.get("MpesaReceiptNumber", ""))
        txn.transaction_date = str(items.get("TransactionDate", ""))
        txn.status = MpesaTransactionStatus.SUCCESS

        # Auto-update invoice
        if txn.invoice_id:
            invoice = db.query(StudentFeeInvoice).filter(
                StudentFeeInvoice.id == txn.invoice_id
            ).first()
            if invoice:
                payment = FeePayment(
                    invoice_id=invoice.id,
                    amount=txn.amount,
                    payment_date=date.today(),
                    payment_method="mpesa",
                    reference=txn.mpesa_receipt_number,
                    note=f"M-Pesa: {txn.mpesa_receipt_number}",
                )
                db.add(payment)
                invoice.paid_amount = min(
                    invoice.paid_amount + txn.amount, invoice.total_amount
                )
                if invoice.paid_amount >= invoice.total_amount:
                    invoice.state = PaymentState.PAID
                else:
                    invoice.state = PaymentState.PARTIAL
    else:
        txn.status = MpesaTransactionStatus.FAILED

    db.commit()
    return {"ResultCode": 0, "ResultDesc": "Accepted"}


@router.get("/mpesa/status/{checkout_request_id}")
def mpesa_status(
    checkout_request_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    txn = db.query(MpesaTransaction).filter(
        MpesaTransaction.checkout_request_id == checkout_request_id
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {
        "status": txn.status.value,
        "receipt": txn.mpesa_receipt_number,
        "amount": txn.amount,
        "result_desc": txn.result_desc,
    }


@router.get("/mpesa/transactions")
def list_transactions(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
):
    txns = db.query(MpesaTransaction).order_by(
        MpesaTransaction.created_at.desc()
    ).offset(skip).limit(limit).all()
    return txns
