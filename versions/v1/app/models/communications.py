"""
Communications models — SMS (Africa's Talking), Announcements, Parent Portal.
"""
import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    ForeignKey, Text, Enum, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


# ── Enums ─────────────────────────────────────────────────────────────────────

class SMSStatus(str, enum.Enum):
    PENDING   = "pending"
    SENT      = "sent"
    DELIVERED = "delivered"
    FAILED    = "failed"


class SMSRecipientType(str, enum.Enum):
    PARENT   = "parent"
    STUDENT  = "student"
    TEACHER  = "teacher"
    STAFF    = "staff"
    CUSTOM   = "custom"


class AnnouncementAudience(str, enum.Enum):
    ALL      = "all"
    PARENTS  = "parents"
    STUDENTS = "students"
    TEACHERS = "teachers"
    STAFF    = "staff"


class AnnouncementPriority(str, enum.Enum):
    LOW    = "low"
    NORMAL = "normal"
    HIGH   = "high"
    URGENT = "urgent"


class ParentMessageStatus(str, enum.Enum):
    UNREAD  = "unread"
    READ    = "read"
    REPLIED = "replied"
    CLOSED  = "closed"


# ── SMS ───────────────────────────────────────────────────────────────────────

class SMSTemplate(Base):
    """Reusable SMS message templates."""
    __tablename__ = "sms_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True)
    body = Column(Text, nullable=False)   # supports {student_name}, {amount}, etc.
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SMSBatch(Base):
    """A bulk SMS send job — one batch can have many recipients."""
    __tablename__ = "sms_batches"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    recipient_type = Column(Enum(SMSRecipientType), nullable=False)
    template_id = Column(Integer, ForeignKey("sms_templates.id"), nullable=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    cost = Column(Float, default=0)          # Africa's Talking cost in KES
    at_batch_id = Column(String(100))        # Africa's Talking messageId
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    template = relationship("SMSTemplate")
    sender = relationship("User")
    logs = relationship("SMSLog", back_populates="batch")


class SMSLog(Base):
    """Individual SMS delivery record per recipient."""
    __tablename__ = "sms_logs"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("sms_batches.id"), nullable=True)
    phone_number = Column(String(20), nullable=False)
    recipient_name = Column(String(200))
    recipient_type = Column(Enum(SMSRecipientType), nullable=True)
    recipient_id = Column(Integer, nullable=True)   # parent_id / student_id / teacher_id
    message = Column(Text, nullable=False)
    status = Column(Enum(SMSStatus), default=SMSStatus.PENDING)
    at_message_id = Column(String(100))             # Africa's Talking messageId
    at_status_code = Column(String(20))
    failure_reason = Column(Text, nullable=True)
    cost = Column(Float, default=0)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    batch = relationship("SMSBatch", back_populates="logs")


# ── Announcements ─────────────────────────────────────────────────────────────

class Announcement(Base):
    """School-wide or targeted announcements."""
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)
    audience = Column(Enum(AnnouncementAudience), default=AnnouncementAudience.ALL)
    priority = Column(Enum(AnnouncementPriority), default=AnnouncementPriority.NORMAL)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)  # class-specific
    is_published = Column(Boolean, default=False)
    publish_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    send_sms = Column(Boolean, default=False)   # also push via SMS
    sms_batch_id = Column(Integer, ForeignKey("sms_batches.id"), nullable=True)
    attachment_url = Column(String(500), nullable=True)
    views = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("User")
    course = relationship("Course")
    sms_batch = relationship("SMSBatch")
    reads = relationship("AnnouncementRead", back_populates="announcement")


class AnnouncementRead(Base):
    """Track which users have read an announcement."""
    __tablename__ = "announcement_reads"

    id = Column(Integer, primary_key=True, index=True)
    announcement_id = Column(Integer, ForeignKey("announcements.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    read_at = Column(DateTime(timezone=True), server_default=func.now())

    announcement = relationship("Announcement", back_populates="reads")


# ── Parent Portal ─────────────────────────────────────────────────────────────

class ParentMessage(Base):
    """
    Direct messaging between parents and school staff.
    Parents can query fees, results, attendance, or raise concerns.
    """
    __tablename__ = "parent_messages"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # staff handling
    subject = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(Enum(ParentMessageStatus), default=ParentMessageStatus.UNREAD)
    is_urgent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    parent = relationship("Parent")
    student = relationship("Student")
    assigned_to = relationship("User")
    replies = relationship("ParentMessageReply", back_populates="message")


class ParentMessageReply(Base):
    """Reply thread on a parent message."""
    __tablename__ = "parent_message_replies"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("parent_messages.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    message = relationship("ParentMessage", back_populates="replies")
    author = relationship("User")


class ParentNotification(Base):
    """
    Push notifications to parents — fee reminders, attendance alerts,
    exam results, disciplinary notices.
    """
    __tablename__ = "parent_notifications"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    notification_type = Column(String(50), default="general")
    # types: fee_reminder, attendance_alert, exam_result, discipline, general
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    sms_sent = Column(Boolean, default=False)
    sms_log_id = Column(Integer, ForeignKey("sms_logs.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent = relationship("Parent")
    student = relationship("Student")
    sms_log = relationship("SMSLog")
