"""LMS endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.lms import OpLmsCourse, OpLmsSection, OpLmsContent, OpLmsEnrollment

router = APIRouter()


@router.get("/lms/courses")
def list_lms_courses(faculty_id: Optional[int] = None, state: Optional[str] = None,
                     db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpLmsCourse).filter_by(active=True)
    if faculty_id: q = q.filter_by(faculty_id=faculty_id)
    if state: q = q.filter_by(state=state)
    return q.all()

@router.post("/lms/courses", status_code=201)
def create_lms_course(name: str, code: str, faculty_id: int,
                      course_id: Optional[int] = None, subject_id: Optional[int] = None,
                      description: Optional[str] = None,
                      db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(OpLmsCourse).filter_by(code=code).first():
        raise HTTPException(409, "LMS course code already exists")
    obj = OpLmsCourse(name=name, code=code, faculty_id=faculty_id, course_id=course_id,
                      subject_id=subject_id, description=description)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/lms/courses/{id}")
def get_lms_course(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpLmsCourse).get(id)
    if not obj: raise HTTPException(404, "LMS course not found")
    return obj

@router.patch("/lms/courses/{id}/publish")
def publish_lms_course(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpLmsCourse).get(id)
    if not obj: raise HTTPException(404, "LMS course not found")
    obj.state = "published"
    db.commit(); db.refresh(obj); return obj


@router.get("/lms/courses/{course_id}/sections")
def list_sections(course_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpLmsSection).filter_by(lms_course_id=course_id).order_by(OpLmsSection.sequence).all()

@router.post("/lms/courses/{course_id}/sections", status_code=201)
def create_section(course_id: int, name: str, sequence: int = 1, description: Optional[str] = None,
                   db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpLmsSection(lms_course_id=course_id, name=name, sequence=sequence, description=description)
    db.add(obj); db.commit(); db.refresh(obj); return obj


@router.get("/lms/sections/{section_id}/contents")
def list_contents(section_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpLmsContent).filter_by(section_id=section_id, active=True).order_by(OpLmsContent.sequence).all()

@router.post("/lms/sections/{section_id}/contents", status_code=201)
def create_content(section_id: int, name: str, content_type: str = "document",
                   resource_url: Optional[str] = None, sequence: int = 1,
                   db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpLmsContent(section_id=section_id, name=name, content_type=content_type,
                       resource_url=resource_url, sequence=sequence)
    db.add(obj); db.commit(); db.refresh(obj); return obj


@router.get("/lms/enrollments")
def list_enrollments(student_id: Optional[int] = None, lms_course_id: Optional[int] = None,
                     db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpLmsEnrollment)
    if student_id: q = q.filter_by(student_id=student_id)
    if lms_course_id: q = q.filter_by(lms_course_id=lms_course_id)
    return q.all()

@router.post("/lms/enrollments", status_code=201)
def enroll_student(student_id: int, lms_course_id: int,
                   db: Session = Depends(get_db), _=Depends(get_current_user)):
    existing = db.query(OpLmsEnrollment).filter_by(student_id=student_id, lms_course_id=lms_course_id).first()
    if existing: raise HTTPException(409, "Already enrolled")
    obj = OpLmsEnrollment(student_id=student_id, lms_course_id=lms_course_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.patch("/lms/enrollments/{id}/progress")
def update_progress(id: int, completion_percentage: float,
                    db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpLmsEnrollment).get(id)
    if not obj: raise HTTPException(404, "Enrollment not found")
    obj.completion_percentage = completion_percentage
    if completion_percentage >= 100:
        obj.status = "completed"
    db.commit(); db.refresh(obj); return obj
