"""Phase 5 seed — SMS templates, announcements, parent messages, notifications."""
import sys, random
from datetime import datetime, timedelta

import app.db.registry  # noqa

from app.db.session import SessionLocal
from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.people import Parent, Student, Teacher
from app.models.communications import (
    SMSTemplate, SMSBatch, SMSLog, SMSStatus, SMSRecipientType,
    Announcement, AnnouncementAudience, AnnouncementPriority,
    ParentMessage, ParentMessageReply, ParentMessageStatus,
    ParentNotification,
)

Base.metadata.create_all(bind=engine)
db = SessionLocal()
print("=== Phase 5 Seed ===")

admin = db.query(User).filter_by(username="admin").first()
parents = db.query(Parent).limit(20).all()
students = db.query(Student).limit(20).all()
teachers = db.query(Teacher).limit(5).all()

if not admin:
    print("[SKIP] No admin user — run seed_kenya.py first")
    sys.exit(0)
print(f"[INFO] {len(parents)} parents, {len(students)} students, {len(teachers)} teachers")

# ── SMS Templates ─────────────────────────────────────────────────────────────
TEMPLATES = [
    ("Fee Reminder",       "FEE_REMINDER",
     "Dear Parent, {student_name}'s school fees balance of KES {amount} is due on {due_date}. Pay via M-Pesa Paybill {paybill}. - {school_name}"),
    ("Attendance Alert",   "ATTENDANCE_ALERT",
     "Dear Parent, {student_name} was marked ABSENT on {date}. Please contact the school if this is an error. - {school_name}"),
    ("Exam Results",       "EXAM_RESULTS",
     "Dear Parent, {student_name} scored {score}% ({grade}) in {exam_name}. Visit the parent portal for full results. - {school_name}"),
    ("General Announcement", "GENERAL_ANNOUNCEMENT",
     "[{school_name}] {message}. Log in to the parent portal for details."),
    ("Fee Receipt",        "FEE_RECEIPT",
     "Dear Parent, payment of KES {amount} received for {student_name}. Receipt No: {receipt_no}. Balance: KES {balance}. - {school_name}"),
    ("Term Dates",         "TERM_DATES",
     "Dear Parent, {term_name} begins on {start_date} and ends on {end_date}. Reporting time: 8:00 AM. - {school_name}"),
    ("Discipline Notice",  "DISCIPLINE_NOTICE",
     "Dear Parent, please report to school on {date} regarding {student_name}. Contact: {phone}. - {school_name}"),
    ("Report Card Ready",  "REPORT_CARD",
     "Dear Parent, {student_name}'s report card for {term_name} is ready. Collect from school or view on parent portal. - {school_name}"),
]
tmpl_count = 0
for name, code, body in TEMPLATES:
    if not db.query(SMSTemplate).filter_by(code=code).first():
        db.add(SMSTemplate(name=name, code=code, body=body))
        tmpl_count += 1
db.commit()
print(f"[OK] {tmpl_count} SMS templates created")

# ── Simulated SMS Batches + Logs ──────────────────────────────────────────────
batch_count = 0
log_count = 0

BATCH_SCENARIOS = [
    ("Term 1 Fee Reminder", "Dear Parent, Term 1 fees are due by 31st January 2026. Pay via M-Pesa Paybill 123456. - CBC EMIS School", "parent"),
    ("Term 1 Opening Announcement", "Dear Parent, Term 1 begins on 6th January 2026. Reporting time 8:00 AM. Bring all required items. - CBC EMIS School", "parent"),
    ("Sports Day Notice", "Dear Parent, Sports Day is on 15th May 2026. Students should come in sports attire. - CBC EMIS School", "parent"),
]

for title, message, rtype in BATCH_SCENARIOS:
    if db.query(SMSBatch).filter_by(title=title).first():
        continue
    recipients = [(p.mobile or p.phone, f"{p.first_name} {p.last_name}", p.id)
                  for p in parents if (p.mobile or p.phone)]
    if not recipients:
        continue
    batch = SMSBatch(
        title=title, message=message,
        recipient_type=SMSRecipientType.PARENT,
        sender_id=admin.id,
        total_recipients=len(recipients),
        sent_count=len(recipients),
        failed_count=0,
        cost=round(len(recipients) * 0.8, 2),
        sent_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
    )
    db.add(batch); db.flush()
    for phone, name, pid in recipients:
        db.add(SMSLog(
            batch_id=batch.id, phone_number=phone,
            recipient_name=name, recipient_type=SMSRecipientType.PARENT,
            recipient_id=pid, message=message,
            status=SMSStatus.DELIVERED,
            at_message_id=f"AT-{batch.id}-{pid}",
            cost=0.8,
            sent_at=batch.sent_at,
            delivered_at=batch.sent_at + timedelta(seconds=random.randint(5, 60)),
        ))
        log_count += 1
    batch_count += 1
db.commit()
print(f"[OK] {batch_count} SMS batches, {log_count} SMS logs created")

# ── Announcements ─────────────────────────────────────────────────────────────
ANNOUNCEMENTS = [
    ("Welcome Back — Term 1 2026",
     "Dear Parents and Students, welcome back to Term 1 2026. We look forward to a productive term. Please ensure all fees are paid by 31st January.",
     "all", "high", True),
    ("Sports Day — 15th May 2026",
     "The annual Sports Day will be held on 15th May 2026. All students are expected to participate. Parents are welcome to attend.",
     "all", "normal", True),
    ("Parent-Teacher Meeting",
     "A Parent-Teacher Meeting is scheduled for 5th June 2026 from 9:00 AM to 1:00 PM. Please make arrangements to attend.",
     "parents", "high", True),
    ("CBC Assessment Guidelines",
     "Teachers are reminded to complete all CBC formative assessments by end of Week 8. Please refer to the updated TPAD guidelines.",
     "teachers", "normal", True),
    ("Library Books Return",
     "All borrowed library books must be returned by 20th March 2026. Fines will be charged for late returns.",
     "students", "normal", True),
    ("School Closure — Public Holiday",
     "The school will be closed on 1st May 2026 (Labour Day). Normal classes resume on 4th May 2026.",
     "all", "urgent", True),
    ("New Digital Classroom Platform",
     "We have launched a new digital classroom platform. Students can access assignments, quizzes, and class materials online. Login details will be shared by class teachers.",
     "all", "normal", True),
    ("Fee Structure 2026",
     "The 2026 fee structure has been approved by the Board of Management. Please collect a copy from the school office or download from the parent portal.",
     "parents", "normal", False),
]
ann_count = 0
for title, body, audience, priority, published in ANNOUNCEMENTS:
    if not db.query(Announcement).filter_by(title=title).first():
        db.add(Announcement(
            title=title, body=body,
            audience=AnnouncementAudience(audience),
            priority=AnnouncementPriority(priority),
            author_id=admin.id,
            is_published=published,
            publish_at=datetime.utcnow() - timedelta(days=random.randint(0, 20)) if published else None,
        ))
        ann_count += 1
db.commit()
print(f"[OK] {ann_count} announcements created")

# ── Parent Messages ───────────────────────────────────────────────────────────
MSG_SUBJECTS = [
    ("Fee Payment Query", "I would like to confirm if my child's fee payment of KES 15,000 made on 10th January has been received and posted to their account."),
    ("Absence Explanation", "My child was absent on Monday 12th January due to a medical appointment. Please find attached the doctor's note."),
    ("Transport Concern", "I am concerned about the school bus arriving late in the evenings. My child has been getting home after 6 PM this week."),
    ("Academic Performance", "I would like to discuss my child's performance in Mathematics. Can we schedule a meeting with the class teacher?"),
    ("Lost Property", "My child lost their school sweater last week. It has their name written inside. Please check the lost and found."),
]
msg_count = 0
reply_count = 0
for i, parent in enumerate(parents[:10]):
    if not parent.students:
        continue
    subject, body = MSG_SUBJECTS[i % len(MSG_SUBJECTS)]
    student = parent.students[0]
    if db.query(ParentMessage).filter_by(parent_id=parent.id, subject=subject).first():
        continue
    status = random.choice([
        ParentMessageStatus.UNREAD, ParentMessageStatus.READ,
        ParentMessageStatus.REPLIED, ParentMessageStatus.REPLIED,
    ])
    msg = ParentMessage(
        parent_id=parent.id,
        student_id=student.id,
        subject=subject,
        body=body,
        status=status,
        is_urgent=(i % 5 == 0),
        assigned_to_id=admin.id,
    )
    db.add(msg); db.flush()
    msg_count += 1
    if status == ParentMessageStatus.REPLIED:
        db.add(ParentMessageReply(
            message_id=msg.id,
            author_id=admin.id,
            body=f"Dear Parent, thank you for reaching out. We have noted your concern regarding '{subject}' and will follow up accordingly. Please feel free to call the school office for further assistance.",
        ))
        reply_count += 1
db.commit()
print(f"[OK] {msg_count} parent messages, {reply_count} replies created")

# ── Parent Notifications ──────────────────────────────────────────────────────
NOTIF_TYPES = [
    ("fee_reminder",    "Fee Reminder",         "Your child's fees balance of KES {bal} is due. Please pay promptly."),
    ("attendance_alert","Attendance Alert",      "Your child was marked absent today. Please contact the school."),
    ("exam_result",     "Exam Results Available","Your child's exam results are now available on the parent portal."),
    ("general",         "School Announcement",  "There is a new announcement on the parent portal. Please log in to view."),
]
notif_count = 0
for i, parent in enumerate(parents[:15]):
    if not parent.students:
        continue
    student = parent.students[0]
    ntype, title, body_tmpl = NOTIF_TYPES[i % len(NOTIF_TYPES)]
    body = body_tmpl.format(bal=f"{random.randint(5, 30) * 1000:,}")
    if not db.query(ParentNotification).filter_by(
            parent_id=parent.id, notification_type=ntype).first():
        db.add(ParentNotification(
            parent_id=parent.id,
            student_id=student.id,
            title=title,
            body=body,
            notification_type=ntype,
            is_read=(i % 3 == 0),
            sms_sent=True,
        ))
        notif_count += 1
db.commit()
print(f"[OK] {notif_count} parent notifications created")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n=== Phase 5 Seed Complete ===")
print(f"  SMS templates       : {tmpl_count}")
print(f"  SMS batches         : {batch_count}")
print(f"  SMS logs            : {log_count}")
print(f"  Announcements       : {ann_count}")
print(f"  Parent messages     : {msg_count}")
print(f"  Message replies     : {reply_count}")
print(f"  Parent notifications: {notif_count}")
db.close()
