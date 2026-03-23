"""Mentorship endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.extras import Mentor, MentorshipGroup, MentorshipMessage
from app.models.people import Student

router = APIRouter()


class MentorCreate(BaseModel):
    user_id: int
    teacher_id: Optional[int] = None
    first_name: str
    last_name: str
    expertise: Optional[str] = None
    bio: Optional[str] = None

class GroupCreate(BaseModel):
    name: str
    mentor_id: int
    description: Optional[str] = None

class MessageCreate(BaseModel):
    content: str


# ── Mentors ───────────────────────────────────────────────────────────────────

@router.get("/mentors")
def list_mentors(db: Session = Depends(get_db), _=Depends(get_current_user)):
    mentors = db.query(Mentor).filter_by(active=True).all()
    return [{"id": m.id, "name": f"{m.first_name} {m.last_name}",
             "expertise": m.expertise, "approved": m.approved,
             "groups_count": len(m.groups)}
            for m in mentors]

@router.post("/mentors", status_code=201)
def create_mentor(data: MentorCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = Mentor(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "name": f"{obj.first_name} {obj.last_name}"}

@router.put("/mentors/{id}/approve")
def approve_mentor(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Mentor).filter_by(id=id).first()
    if not obj: raise HTTPException(404, "Mentor not found")
    obj.approved = True; db.commit()
    return {"id": obj.id, "approved": True}


# ── Groups ────────────────────────────────────────────────────────────────────

@router.get("/groups")
def list_groups(db: Session = Depends(get_db), _=Depends(get_current_user)):
    groups = db.query(MentorshipGroup).filter_by(active=True).all()
    return [{"id": g.id, "name": g.name,
             "mentor": f"{g.mentor.first_name} {g.mentor.last_name}" if g.mentor else None,
             "students_count": len(g.students)}
            for g in groups]

@router.post("/groups", status_code=201)
def create_group(data: GroupCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = MentorshipGroup(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "name": obj.name}

@router.get("/groups/{id}")
def get_group(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(MentorshipGroup).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Group not found")
    return {"id": obj.id, "name": obj.name, "description": obj.description,
            "mentor": f"{obj.mentor.first_name} {obj.mentor.last_name}" if obj.mentor else None,
            "students": [{"id": s.id, "name": f"{s.first_name} {s.last_name}"}
                         for s in obj.students]}

@router.post("/groups/{id}/students/{student_id}", status_code=201)
def add_student(id: int, student_id: int, db: Session = Depends(get_db),
                _=Depends(get_current_user)):
    group = db.query(MentorshipGroup).filter_by(id=id, active=True).first()
    if not group: raise HTTPException(404, "Group not found")
    student = db.query(Student).filter_by(id=student_id).first()
    if not student: raise HTTPException(404, "Student not found")
    if student in group.students: raise HTTPException(400, "Student already in group")
    group.students.append(student); db.commit()
    return {"group_id": id, "student_id": student_id}

@router.delete("/groups/{id}/students/{student_id}", status_code=204)
def remove_student(id: int, student_id: int, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
    group = db.query(MentorshipGroup).filter_by(id=id, active=True).first()
    if not group: raise HTTPException(404, "Group not found")
    student = db.query(Student).filter_by(id=student_id).first()
    if student and student in group.students:
        group.students.remove(student); db.commit()


# ── Messages ──────────────────────────────────────────────────────────────────

@router.get("/groups/{id}/messages")
def list_messages(id: int, skip: int = 0, limit: int = 50,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    msgs = (db.query(MentorshipMessage).filter_by(group_id=id)
            .order_by(MentorshipMessage.created_at.desc())
            .offset(skip).limit(limit).all())
    return [{"id": m.id, "sender_id": m.sender_id,
             "sender": f"{m.sender.first_name} {m.sender.last_name}" if m.sender else None,
             "content": m.content, "created_at": m.created_at}
            for m in msgs]

@router.post("/groups/{id}/messages", status_code=201)
def post_message(id: int, data: MessageCreate, db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    group = db.query(MentorshipGroup).filter_by(id=id, active=True).first()
    if not group: raise HTTPException(404, "Group not found")
    msg = MentorshipMessage(group_id=id, sender_id=current_user.id, content=data.content)
    db.add(msg); db.commit(); db.refresh(msg)
    return {"id": msg.id, "group_id": id, "created_at": msg.created_at}
