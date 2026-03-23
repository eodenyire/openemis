"""SMS endpoints — Africa's Talking bulk SMS, templates, delivery logs."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.communications import (
    SMSTemplate, SMSBatch, SMSLog, SMSStatus, SMSRecipientType,
)
from app.models.people import Parent, Student, Teacher
from app.services.sms import send_sms, parse_at_response

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class TemplateCreate(BaseModel):
    name: str
    code: str
    body: str
    description: Optional[str] = None

class TemplateOut(BaseModel):
    id: int; name: str; code: str; body: str; is_active: bool
    class Config: from_attributes = True

class SMSSendRequest(BaseModel):
    title: str
    message: str
    recipient_type: str          # parent | student | teacher | staff | custom
    custom_phones: Optional[List[str]] = None   # used when recipient_type=custom
    course_id: Optional[int] = None             # filter by class
    template_id: Optional[int] = None

class SMSLogOut(BaseModel):
    id: int; phone_number: str; recipient_name: Optional[str]
    message: str; status: str; cost: float
    sent_at: Optional[datetime]
    class Config: from_attributes = True

class SMSBatchOut(BaseModel):
    id: int; title: str; recipient_type: str
    total_recipients: int; sent_count: int; failed_count: int
    cost: float; sent_at: Optional[datetime]
    class Config: from_attributes = True


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_phones(db: Session, recipient_type: str,
                course_id: Optional[int], custom_phones: Optional[List[str]]):
    """Return list of (phone, name, type, id) tuples."""
    results = []
    if recipient_type == "custom" and custom_phones:
        return [(p, "Custom", "custom", None) for p in custom_phones]
    if recipient_type == "parent":
        q = db.query(Parent)
        parents = q.all()
        for p in parents:
            phone = p.mobile or p.phone
            if phone:
                results.append((phone, f"{p.first_name} {p.last_name}", "parent", p.id))
    elif recipient_type == "student":
        q = db.query(Student)
        if course_id:
            from app.models.core import Course
            from app.models.people import StudentCourse
            q = q.join(StudentCourse).filter(StudentCourse.course_id == course_id)
        for s in q.all():
            phone = s.mobile or s.phone
            if phone:
                results.append((phone, f"{s.first_name} {s.last_name}", "student", s.id))
    elif recipient_type == "teacher":
        for t in db.query(Teacher).filter_by(active=True).all():
            phone = t.mobile or t.phone
            if phone:
                results.append((phone, f"{t.first_name} {t.last_name}", "teacher", t.id))
    return results


# ── SMS Templates ─────────────────────────────────────────────────────────────

@router.get("/templates", response_model=List[TemplateOut])
def list_templates(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(SMSTemplate).filter_by(is_active=True).all()

@router.post("/templates", response_model=TemplateOut, status_code=201)
def create_template(data: TemplateCreate, db: Session = Depends(get_db),
                    _=Depends(require_admin)):
    if db.query(SMSTemplate).filter_by(code=data.code).first():
        raise HTTPException(409, f"Template '{data.code}' already exists")
    obj = SMSTemplate(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/templates/{id}", response_model=TemplateOut)
def update_template(id: int, data: TemplateCreate, db: Session = Depends(get_db),
                    _=Depends(require_admin)):
    obj = db.query(SMSTemplate).get(id)
    if not obj: raise HTTPException(404, "Template not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/templates/{id}", status_code=204)
def delete_template(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(SMSTemplate).get(id)
    if not obj: raise HTTPException(404, "Template not found")
    obj.is_active = False
    db.commit()


# ── Send SMS ──────────────────────────────────────────────────────────────────

@router.post("/send", status_code=202)
async def send_bulk_sms(data: SMSSendRequest, background_tasks: BackgroundTasks,
                        db: Session = Depends(get_db),
                        current_user=Depends(get_current_user)):
    """
    Send bulk SMS to parents, students, teachers, or custom numbers.
    Uses Africa's Talking API. Runs delivery in background.
    """
    recipients = _get_phones(db, data.recipient_type, data.course_id, data.custom_phones)
    if not recipients:
        raise HTTPException(400, "No recipients with phone numbers found")

    # Create batch record
    batch = SMSBatch(
        title=data.title,
        message=data.message,
        recipient_type=SMSRecipientType(data.recipient_type),
        template_id=data.template_id,
        sender_id=current_user.id,
        total_recipients=len(recipients),
    )
    db.add(batch); db.commit(); db.refresh(batch)

    # Create pending log entries
    for phone, name, rtype, rid in recipients:
        db.add(SMSLog(
            batch_id=batch.id,
            phone_number=phone,
            recipient_name=name,
            recipient_type=SMSRecipientType(rtype) if rtype != "custom" else None,
            recipient_id=rid,
            message=data.message,
            status=SMSStatus.PENDING,
        ))
    db.commit()

    # Fire and forget — send via AT in background
    background_tasks.add_task(
        _dispatch_sms_batch, batch.id, [r[0] for r in recipients], data.message
    )

    return {
        "batch_id": batch.id,
        "total_recipients": len(recipients),
        "status": "queued",
        "message": f"SMS queued for {len(recipients)} recipients",
    }


async def _dispatch_sms_batch(batch_id: int, phones: List[str], message: str):
    """Background task — calls AT API and updates log records."""
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        response = await send_sms(phones, message)
        parsed = parse_at_response(response)
        batch = db.query(SMSBatch).get(batch_id)
        if batch:
            batch.sent_count = parsed["sent"]
            batch.failed_count = parsed["failed"]
            batch.cost = parsed["cost"]
            batch.sent_at = datetime.utcnow()

        # Update individual log statuses
        for rec in parsed["recipients"]:
            phone = rec.get("number", "")
            log = db.query(SMSLog).filter_by(
                batch_id=batch_id, phone_number=phone).first()
            if not log:
                # try normalized
                from app.services.sms import _normalize_phone
                log = db.query(SMSLog).filter_by(
                    batch_id=batch_id,
                    phone_number=_normalize_phone(phone)).first()
            if log:
                log.status = (SMSStatus.SENT if rec.get("status") == "Success"
                              else SMSStatus.FAILED)
                log.at_message_id = rec.get("messageId")
                log.at_status_code = rec.get("statusCode")
                log.cost = float(rec.get("cost", "KES 0").replace("KES", "").strip() or 0)
                log.sent_at = datetime.utcnow()
        db.commit()
    except Exception as e:
        # Mark batch as failed
        batch = db.query(SMSBatch).get(batch_id)
        if batch:
            batch.failed_count = batch.total_recipients
            db.commit()
    finally:
        db.close()


@router.post("/send-single")
async def send_single(phone: str, message: str,
                      db: Session = Depends(get_db),
                      current_user=Depends(get_current_user)):
    """Send a one-off SMS to a single number."""
    from app.services.sms import send_single_sms
    response = await send_single_sms(phone, message)
    parsed = parse_at_response(response)
    log = SMSLog(
        phone_number=phone,
        message=message,
        status=SMSStatus.SENT if parsed["sent"] > 0 else SMSStatus.FAILED,
        cost=parsed["cost"],
        sent_at=datetime.utcnow(),
    )
    db.add(log); db.commit()
    return {"status": log.status, "cost": parsed["cost"], "log_id": log.id}


# ── Delivery Reports ──────────────────────────────────────────────────────────

@router.post("/delivery-report")
async def delivery_report(request_data: dict, db: Session = Depends(get_db)):
    """Africa's Talking delivery report webhook."""
    msg_id = request_data.get("id")
    status = request_data.get("status", "").lower()
    if msg_id:
        log = db.query(SMSLog).filter_by(at_message_id=msg_id).first()
        if log:
            log.status = SMSStatus.DELIVERED if "delivered" in status else SMSStatus.FAILED
            if "delivered" in status:
                log.delivered_at = datetime.utcnow()
            db.commit()
    return {"ok": True}


# ── Batches & Logs ────────────────────────────────────────────────────────────

@router.get("/batches", response_model=List[SMSBatchOut])
def list_batches(skip: int = 0, limit: int = 50, db: Session = Depends(get_db),
                 _=Depends(get_current_user)):
    return db.query(SMSBatch).order_by(
        SMSBatch.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/batches/{id}", response_model=SMSBatchOut)
def get_batch(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(SMSBatch).get(id)
    if not obj: raise HTTPException(404, "Batch not found")
    return obj

@router.get("/batches/{id}/logs", response_model=List[SMSLogOut])
def batch_logs(id: int, skip: int = 0, limit: int = 200,
               db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(SMSLog).filter_by(batch_id=id).offset(skip).limit(limit).all()

@router.get("/logs", response_model=List[SMSLogOut])
def all_logs(skip: int = 0, limit: int = 100,
             status: Optional[str] = None,
             db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(SMSLog)
    if status: q = q.filter(SMSLog.status == status)
    return q.order_by(SMSLog.created_at.desc()).offset(skip).limit(limit).all()
