"""
Parent Portal endpoints — parent dashboard, messaging, notifications,
fee status, attendance summary, exam results, child overview.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.communications import (
    ParentMessage, ParentMessageReply, ParentNotification,
    ParentMessageStatus,
)
from app.models.people import Parent, StudentCourse
from app.models.fees import StudentFeeInvoice
from app.models.attendance import AttendanceLine, AttendanceSheet, AttendanceStatus
from app.models.exam import ExamAttendees

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    student_id: Optional[int] = None
    subject: str
    body: str
    is_urgent: bool = False

class MessageOut(BaseModel):
    id: int; parent_id: int; subject: str; body: str
    status: str; is_urgent: bool; created_at: datetime
    student_id: Optional[int]
    class Config: from_attributes = True

class ReplyCreate(BaseModel):
    body: str

class ReplyOut(BaseModel):
    id: int; message_id: int; body: str; created_at: datetime
    author_id: int
    class Config: from_attributes = True

class NotificationOut(BaseModel):
    id: int; title: str; body: str; notification_type: str
    is_read: bool; created_at: datetime; student_id: Optional[int]
    class Config: from_attributes = True


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_parent(db: Session, user_id: int) -> Parent:
    parent = db.query(Parent).filter_by(user_id=user_id).first()
    if not parent:
        raise HTTPException(403, "Parent profile not found for this user")
    return parent


# ── Parent Dashboard ──────────────────────────────────────────────────────────

@router.get("/dashboard")
def parent_dashboard(db: Session = Depends(get_db),
                     current_user=Depends(get_current_user)):
    parent = _get_parent(db, current_user.id)
    children = parent.students

    dashboard = {
        "parent_id": parent.id,
        "parent_name": f"{parent.first_name} {parent.last_name}",
        "children": [],
        "unread_notifications": db.query(ParentNotification).filter_by(
            parent_id=parent.id, is_read=False).count(),
        "open_messages": db.query(ParentMessage).filter_by(
            parent_id=parent.id).filter(
            ParentMessage.status != ParentMessageStatus.CLOSED).count(),
    }

    for child in children:
        # Fee balance — use correct field names: total_amount, paid_amount, state
        invoices = db.query(StudentFeeInvoice).filter_by(student_id=child.id).all()
        total_fees = sum(float(inv.total_amount or 0) for inv in invoices)
        total_paid = sum(float(inv.paid_amount or 0) for inv in invoices)
        balance = total_fees - total_paid

        # Attendance — status enum, join via sheet_id → AttendanceSheet
        present = (db.query(AttendanceLine)
                   .filter_by(student_id=child.id, status=AttendanceStatus.PRESENT)
                   .count())
        absent = (db.query(AttendanceLine)
                  .filter_by(student_id=child.id, status=AttendanceStatus.ABSENT)
                  .count())

        enrollment = db.query(StudentCourse).filter_by(
            student_id=child.id, state="running").first()

        dashboard["children"].append({
            "student_id": child.id,
            "name": f"{child.first_name} {child.last_name}",
            "admission_number": child.admission_number,
            "class": enrollment.course.name if enrollment else None,
            "fees": {
                "total": total_fees,
                "paid": total_paid,
                "balance": balance,
            },
            "attendance": {
                "present": present,
                "absent": absent,
                "rate": round(present / (present + absent) * 100, 1) if (present + absent) > 0 else 0,
            },
        })

    return dashboard


@router.get("/children")
def list_children(db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    parent = _get_parent(db, current_user.id)
    return [
        {
            "id": s.id,
            "name": f"{s.first_name} {s.last_name}",
            "admission_number": s.admission_number,
            "nemis_upi": s.nemis_upi,
        }
        for s in parent.students
    ]


@router.get("/children/{student_id}/fees")
def child_fees(student_id: int, db: Session = Depends(get_db),
               current_user=Depends(get_current_user)):
    parent = _get_parent(db, current_user.id)
    if student_id not in [s.id for s in parent.students]:
        raise HTTPException(403, "Not your child")
    invoices = db.query(StudentFeeInvoice).filter_by(student_id=student_id).all()
    return [
        {
            "id": inv.id,
            "total_amount": float(inv.total_amount or 0),
            "paid_amount": float(inv.paid_amount or 0),
            "balance": float((inv.total_amount or 0) - (inv.paid_amount or 0)),
            "due_date": inv.due_date,
            "state": inv.state,
        }
        for inv in invoices
    ]


@router.get("/children/{student_id}/attendance")
def child_attendance(student_id: int, limit: int = 30,
                     db: Session = Depends(get_db),
                     current_user=Depends(get_current_user)):
    parent = _get_parent(db, current_user.id)
    if student_id not in [s.id for s in parent.students]:
        raise HTTPException(403, "Not your child")
    lines = (db.query(AttendanceLine)
             .filter_by(student_id=student_id)
             .join(AttendanceSheet, AttendanceLine.sheet_id == AttendanceSheet.id)
             .order_by(AttendanceSheet.attendance_date.desc())
             .limit(limit).all())
    return [
        {
            "date": line.sheet.attendance_date,
            "status": line.status,
            "note": line.note,
        }
        for line in lines
    ]


@router.get("/children/{student_id}/results")
def child_results(student_id: int, db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    parent = _get_parent(db, current_user.id)
    if student_id not in [s.id for s in parent.students]:
        raise HTTPException(403, "Not your child")
    results = db.query(ExamAttendees).filter_by(student_id=student_id).all()
    return [
        {
            "exam_id": r.exam_id,
            "marks": float(r.marks or 0),
            "state": r.state,
        }
        for r in results
    ]


# ── Messaging ─────────────────────────────────────────────────────────────────

@router.get("/messages", response_model=List[MessageOut])
def list_messages(db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    parent = _get_parent(db, current_user.id)
    return db.query(ParentMessage).filter_by(parent_id=parent.id).order_by(
        ParentMessage.created_at.desc()).all()

@router.post("/messages", response_model=MessageOut, status_code=201)
def create_message(data: MessageCreate, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    parent = _get_parent(db, current_user.id)
    if data.student_id and data.student_id not in [s.id for s in parent.students]:
        raise HTTPException(403, "Not your child")
    obj = ParentMessage(parent_id=parent.id, **data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/messages/{id}", response_model=MessageOut)
def get_message(id: int, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    parent = _get_parent(db, current_user.id)
    obj = db.query(ParentMessage).filter_by(id=id, parent_id=parent.id).first()
    if not obj: raise HTTPException(404, "Message not found")
    return obj

@router.post("/messages/{id}/reply", response_model=ReplyOut, status_code=201)
def reply_message(id: int, data: ReplyCreate, db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    msg = db.query(ParentMessage).get(id)
    if not msg: raise HTTPException(404, "Message not found")
    reply = ParentMessageReply(message_id=id, author_id=current_user.id, body=data.body)
    db.add(reply)
    msg.status = ParentMessageStatus.REPLIED
    db.commit(); db.refresh(reply)
    return reply

@router.get("/messages/{id}/replies", response_model=List[ReplyOut])
def list_replies(id: int, db: Session = Depends(get_db),
                 _=Depends(get_current_user)):
    return db.query(ParentMessageReply).filter_by(message_id=id).order_by(
        ParentMessageReply.created_at).all()

@router.put("/messages/{id}/close")
def close_message(id: int, db: Session = Depends(get_db),
                  _=Depends(get_current_user)):
    msg = db.query(ParentMessage).get(id)
    if not msg: raise HTTPException(404, "Message not found")
    msg.status = ParentMessageStatus.CLOSED
    db.commit()
    return {"id": msg.id, "status": msg.status}


# ── Staff: view all parent messages ──────────────────────────────────────────

@router.get("/staff/messages")
def staff_view_messages(skip: int = 0, limit: int = 50,
                        status: Optional[str] = None,
                        db: Session = Depends(get_db),
                        _=Depends(get_current_user)):
    q = db.query(ParentMessage)
    if status:
        q = q.filter(ParentMessage.status == status)
    msgs = q.order_by(ParentMessage.is_urgent.desc(),
                      ParentMessage.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {"id": m.id, "parent_id": m.parent_id, "subject": m.subject,
         "status": m.status, "is_urgent": m.is_urgent, "created_at": m.created_at}
        for m in msgs
    ]

@router.put("/staff/messages/{id}/assign")
def assign_message(id: int, staff_user_id: int, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
    msg = db.query(ParentMessage).get(id)
    if not msg: raise HTTPException(404, "Message not found")
    msg.assigned_to_id = staff_user_id
    db.commit()
    return {"id": msg.id, "assigned_to_id": msg.assigned_to_id}


# ── Notifications ─────────────────────────────────────────────────────────────

@router.get("/notifications", response_model=List[NotificationOut])
def list_notifications(skip: int = 0, limit: int = 50,
                       unread_only: bool = False,
                       db: Session = Depends(get_db),
                       current_user=Depends(get_current_user)):
    parent = _get_parent(db, current_user.id)
    q = db.query(ParentNotification).filter_by(parent_id=parent.id)
    if unread_only:
        q = q.filter_by(is_read=False)
    return q.order_by(ParentNotification.created_at.desc()).offset(skip).limit(limit).all()

@router.put("/notifications/{id}/read")
def mark_notification_read(id: int, db: Session = Depends(get_db),
                            current_user=Depends(get_current_user)):
    parent = _get_parent(db, current_user.id)
    notif = db.query(ParentNotification).filter_by(id=id, parent_id=parent.id).first()
    if not notif: raise HTTPException(404, "Notification not found")
    notif.is_read = True
    notif.read_at = datetime.utcnow()
    db.commit()
    return {"id": notif.id, "is_read": True}

@router.put("/notifications/read-all")
def mark_all_read(db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    parent = _get_parent(db, current_user.id)
    db.query(ParentNotification).filter_by(
        parent_id=parent.id, is_read=False).update(
        {"is_read": True, "read_at": datetime.utcnow()})
    db.commit()
    return {"status": "all notifications marked as read"}


# ── Staff: send notification ──────────────────────────────────────────────────

class NotificationCreate(BaseModel):
    parent_id: int
    student_id: Optional[int] = None
    title: str
    body: str
    notification_type: str = "general"
    send_sms: bool = False

@router.post("/notifications/send", status_code=201)
async def send_notification(data: NotificationCreate,
                            db: Session = Depends(get_db),
                            current_user=Depends(get_current_user)):
    notif = ParentNotification(
        parent_id=data.parent_id,
        student_id=data.student_id,
        title=data.title,
        body=data.body,
        notification_type=data.notification_type,
    )
    db.add(notif); db.flush()

    if data.send_sms:
        parent = db.query(Parent).get(data.parent_id)
        if parent:
            phone = parent.mobile or parent.phone
            if phone:
                from app.services.sms import send_single_sms
                try:
                    await send_single_sms(phone, f"{data.title}: {data.body[:100]}")
                    notif.sms_sent = True
                except Exception:
                    pass

    db.commit(); db.refresh(notif)
    return {"id": notif.id, "sms_sent": notif.sms_sent}
