"""Announcements endpoints — school-wide and targeted announcements."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.communications import (
    Announcement, AnnouncementRead,
    AnnouncementAudience, AnnouncementPriority,
    SMSBatch, SMSLog, SMSStatus, SMSRecipientType,
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class AnnouncementCreate(BaseModel):
    title: str
    body: str
    audience: str = "all"
    priority: str = "normal"
    course_id: Optional[int] = None
    is_published: bool = False
    publish_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    send_sms: bool = False
    attachment_url: Optional[str] = None

class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    audience: Optional[str] = None
    priority: Optional[str] = None
    is_published: Optional[bool] = None
    expires_at: Optional[datetime] = None
    send_sms: Optional[bool] = None

class AnnouncementOut(BaseModel):
    id: int; title: str; body: str; audience: str; priority: str
    author_id: int; is_published: bool; views: int
    send_sms: bool; course_id: Optional[int]
    created_at: datetime
    class Config: from_attributes = True


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[AnnouncementOut])
def list_announcements(skip: int = 0, limit: int = 50,
                       audience: Optional[str] = None,
                       published_only: bool = True,
                       db: Session = Depends(get_db),
                       _=Depends(get_current_user)):
    q = db.query(Announcement)
    if published_only:
        q = q.filter_by(is_published=True)
    if audience:
        q = q.filter(Announcement.audience == audience)
    return q.order_by(Announcement.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/", response_model=AnnouncementOut, status_code=201)
async def create_announcement(data: AnnouncementCreate,
                               background_tasks: BackgroundTasks,
                               db: Session = Depends(get_db),
                               current_user=Depends(get_current_user)):
    obj = Announcement(
        **data.model_dump(exclude={"send_sms"}),
        author_id=current_user.id,
        send_sms=data.send_sms,
    )
    db.add(obj); db.commit(); db.refresh(obj)

    # If send_sms=True and published, queue SMS in background
    if data.send_sms and data.is_published:
        background_tasks.add_task(_send_announcement_sms, obj.id, data.audience)

    return obj

@router.get("/{id}", response_model=AnnouncementOut)
def get_announcement(id: int, db: Session = Depends(get_db),
                     current_user=Depends(get_current_user)):
    obj = db.query(Announcement).get(id)
    if not obj: raise HTTPException(404, "Announcement not found")
    # Track view
    already_read = db.query(AnnouncementRead).filter_by(
        announcement_id=id, user_id=current_user.id).first()
    if not already_read:
        db.add(AnnouncementRead(announcement_id=id, user_id=current_user.id))
        obj.views = (obj.views or 0) + 1
        db.commit()
    return obj

@router.put("/{id}", response_model=AnnouncementOut)
def update_announcement(id: int, data: AnnouncementUpdate,
                         db: Session = Depends(get_db),
                         _=Depends(get_current_user)):
    obj = db.query(Announcement).get(id)
    if not obj: raise HTTPException(404, "Announcement not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/{id}", status_code=204)
def delete_announcement(id: int, db: Session = Depends(get_db),
                         _=Depends(require_admin)):
    obj = db.query(Announcement).get(id)
    if not obj: raise HTTPException(404, "Announcement not found")
    db.delete(obj); db.commit()

@router.put("/{id}/publish")
async def publish_announcement(id: int, send_sms: bool = False,
                                background_tasks: BackgroundTasks = None,
                                db: Session = Depends(get_db),
                                _=Depends(get_current_user)):
    obj = db.query(Announcement).get(id)
    if not obj: raise HTTPException(404, "Announcement not found")
    obj.is_published = True
    obj.publish_at = datetime.utcnow()
    if send_sms:
        obj.send_sms = True
    db.commit()
    if send_sms and background_tasks:
        background_tasks.add_task(_send_announcement_sms, id, obj.audience.value)
    return {"id": obj.id, "is_published": True}

@router.get("/{id}/reads")
def announcement_reads(id: int, db: Session = Depends(get_db),
                        _=Depends(get_current_user)):
    reads = db.query(AnnouncementRead).filter_by(announcement_id=id).count()
    obj = db.query(Announcement).get(id)
    return {"announcement_id": id, "total_reads": reads,
            "total_views": obj.views if obj else 0}


# ── Background SMS dispatch ───────────────────────────────────────────────────

async def _send_announcement_sms(announcement_id: int, audience: str):
    from app.db.session import SessionLocal
    from app.services.sms import send_sms, parse_at_response, build_announcement_sms
    from app.models.people import Parent, Teacher
    db = SessionLocal()
    try:
        ann = db.query(Announcement).get(announcement_id)
        if not ann: return

        phones = []
        if audience in ("all", "parents"):
            for p in db.query(Parent).all():
                ph = p.mobile or p.phone
                if ph: phones.append(ph)
        if audience in ("all", "teachers"):
            for t in db.query(Teacher).filter_by(active=True).all():
                ph = t.mobile or t.phone
                if ph: phones.append(ph)

        if not phones: return

        message = build_announcement_sms(ann.title)
        response = await send_sms(phones, message)
        parsed = parse_at_response(response)

        batch = SMSBatch(
            title=f"Announcement: {ann.title[:80]}",
            message=message,
            recipient_type=SMSRecipientType.PARENT,
            sender_id=ann.author_id,
            total_recipients=len(phones),
            sent_count=parsed["sent"],
            failed_count=parsed["failed"],
            cost=parsed["cost"],
            sent_at=datetime.utcnow(),
        )
        db.add(batch); db.flush()
        ann.sms_batch_id = batch.id
        db.commit()
    except Exception:
        pass
    finally:
        db.close()
