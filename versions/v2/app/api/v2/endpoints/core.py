"""Core endpoints — departments, programs, academic years/terms, courses, subjects, batches, students, faculty."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.core import (
    OpDepartment, OpProgram, OpAcademicYear, OpAcademicTerm,
    OpCourse, OpSubject, OpBatch, OpStudent, OpFaculty, OpStudentCourse, OpCategory,
)

router = APIRouter()


# ── Departments ───────────────────────────────────────────────────────────────
@router.get("/departments")
def list_departments(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpDepartment).filter_by(active=True).all()

@router.post("/departments", status_code=201)
def create_department(name: str, code: Optional[str] = None, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpDepartment(name=name, code=code)
    db.add(obj); db.commit(); db.refresh(obj); return obj


# ── Programs ──────────────────────────────────────────────────────────────────
@router.get("/programs")
def list_programs(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpProgram).filter_by(active=True).all()

@router.post("/programs", status_code=201)
def create_program(name: str, code: Optional[str] = None, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpProgram(name=name, code=code)
    db.add(obj); db.commit(); db.refresh(obj); return obj


# ── Academic Years ────────────────────────────────────────────────────────────
@router.get("/academic-years")
def list_academic_years(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpAcademicYear).filter_by(active=True).all()

@router.post("/academic-years", status_code=201)
def create_academic_year(name: str, start_date: Optional[date] = None, end_date: Optional[date] = None,
                         db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpAcademicYear(name=name, start_date=start_date, end_date=end_date)
    db.add(obj); db.commit(); db.refresh(obj); return obj


# ── Academic Terms ────────────────────────────────────────────────────────────
@router.get("/academic-terms")
def list_academic_terms(academic_year_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpAcademicTerm).filter_by(active=True)
    if academic_year_id: q = q.filter_by(academic_year_id=academic_year_id)
    return q.all()

@router.post("/academic-terms", status_code=201)
def create_academic_term(name: str, academic_year_id: int, start_date: Optional[date] = None,
                         end_date: Optional[date] = None, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpAcademicTerm(name=name, academic_year_id=academic_year_id, start_date=start_date, end_date=end_date)
    db.add(obj); db.commit(); db.refresh(obj); return obj


# ── Courses ───────────────────────────────────────────────────────────────────
@router.get("/courses")
def list_courses(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpCourse).filter_by(active=True).all()

@router.post("/courses", status_code=201)
def create_course(name: str, code: str, evaluation_type: str = "normal",
                  department_id: Optional[int] = None, program_id: Optional[int] = None,
                  db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(OpCourse).filter_by(code=code).first():
        raise HTTPException(409, "Course code already exists")
    obj = OpCourse(name=name, code=code, evaluation_type=evaluation_type,
                   department_id=department_id, program_id=program_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/courses/{id}")
def get_course(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpCourse).get(id)
    if not obj: raise HTTPException(404, "Course not found")
    return obj


# ── Subjects ──────────────────────────────────────────────────────────────────
@router.get("/subjects")
def list_subjects(course_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpSubject).filter_by(active=True)
    if course_id:
        course = db.query(OpCourse).get(course_id)
        return course.subjects if course else []
    return q.all()

@router.post("/subjects", status_code=201)
def create_subject(name: str, code: str, subject_type: str = "theory",
                   department_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(OpSubject).filter_by(code=code).first():
        raise HTTPException(409, "Subject code already exists")
    obj = OpSubject(name=name, code=code, subject_type=subject_type, department_id=department_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj


# ── Batches ───────────────────────────────────────────────────────────────────
@router.get("/batches")
def list_batches(course_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpBatch).filter_by(active=True)
    if course_id: q = q.filter_by(course_id=course_id)
    return q.all()

@router.post("/batches", status_code=201)
def create_batch(name: str, code: str, course_id: int, start_date: Optional[date] = None,
                 end_date: Optional[date] = None, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpBatch(name=name, code=code, course_id=course_id, start_date=start_date, end_date=end_date)
    db.add(obj); db.commit(); db.refresh(obj); return obj


# ── Students ──────────────────────────────────────────────────────────────────
@router.get("/students")
def list_students(skip: int = 0, limit: int = 100, search: Optional[str] = None,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpStudent).filter_by(active=True)
    if search:
        q = q.filter(OpStudent.first_name.ilike(f"%{search}%") | OpStudent.last_name.ilike(f"%{search}%"))
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": s.id, "first_name": s.first_name, "last_name": s.last_name,
         "gr_no": s.gr_no, "gender": s.gender, "email": s.email} for s in items
    ]}

@router.post("/students", status_code=201)
def create_student(first_name: str, last_name: str, birth_date: Optional[date] = None,
                   gender: Optional[str] = None, email: Optional[str] = None,
                   gr_no: Optional[str] = None, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpStudent(first_name=first_name, last_name=last_name, birth_date=birth_date,
                    gender=gender, email=email, gr_no=gr_no)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/students/{id}")
def get_student(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpStudent).get(id)
    if not obj: raise HTTPException(404, "Student not found")
    return obj


# ── Faculty ───────────────────────────────────────────────────────────────────
@router.get("/faculty")
def list_faculty(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(get_current_user)):
    items = db.query(OpFaculty).filter_by(active=True).offset(skip).limit(limit).all()
    return [{"id": f.id, "first_name": f.first_name, "last_name": f.last_name,
             "emp_id": f.emp_id, "email": f.email} for f in items]

@router.post("/faculty", status_code=201)
def create_faculty(first_name: str, last_name: str, emp_id: Optional[str] = None,
                   email: Optional[str] = None, department_id: Optional[int] = None,
                   db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpFaculty(first_name=first_name, last_name=last_name, emp_id=emp_id,
                    email=email, main_department_id=department_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj


# ── Student Course Enrollment ─────────────────────────────────────────────────
@router.post("/enrollments", status_code=201)
def enroll_student(student_id: int, course_id: int, batch_id: Optional[int] = None,
                   roll_number: Optional[str] = None, academic_year_id: Optional[int] = None,
                   db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpStudentCourse(student_id=student_id, course_id=course_id, batch_id=batch_id,
                          roll_number=roll_number, academic_year_id=academic_year_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/enrollments")
def list_enrollments(course_id: Optional[int] = None, batch_id: Optional[int] = None,
                     db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpStudentCourse)
    if course_id: q = q.filter_by(course_id=course_id)
    if batch_id: q = q.filter_by(batch_id=batch_id)
    return q.all()
