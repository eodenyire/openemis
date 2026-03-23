"""People endpoints: teachers, students, enrollments, parents"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin, require_teacher
from app.api.crud import get_one, get_all, create_obj, update_obj, delete_obj
from app.models.people import Teacher, Student, StudentCourse, Parent, ParentRelationship
from app.schemas.people import (
    TeacherCreate, TeacherUpdate, TeacherOut,
    StudentCreate, StudentUpdate, StudentOut,
    StudentCourseCreate, StudentCourseUpdate, StudentCourseOut,
    ParentCreate, ParentUpdate, ParentOut,
    ParentRelationshipCreate, ParentRelationshipOut,
)

router = APIRouter()


# ── Teachers ──────────────────────────────────────────────────────────────────
@router.get("/teachers/", response_model=List[TeacherOut], tags=["Teachers"])
def list_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                  _=Depends(get_current_user)):
    return get_all(db, Teacher, skip, limit)

@router.post("/teachers/", response_model=TeacherOut, status_code=201, tags=["Teachers"])
def create_teacher(data: TeacherCreate, db: Session = Depends(get_db),
                   _=Depends(require_admin)):
    return create_obj(db, Teacher, data.model_dump())

@router.get("/teachers/{id}", response_model=TeacherOut, tags=["Teachers"])
def get_teacher(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, Teacher, id)
    if not obj: raise HTTPException(404, "Teacher not found")
    return obj

@router.put("/teachers/{id}", response_model=TeacherOut, tags=["Teachers"])
def update_teacher(id: int, data: TeacherUpdate, db: Session = Depends(get_db),
                   _=Depends(require_admin)):
    obj = get_one(db, Teacher, id)
    if not obj: raise HTTPException(404, "Teacher not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/teachers/{id}", status_code=204, tags=["Teachers"])
def delete_teacher(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Teacher, id)
    if not obj: raise HTTPException(404, "Teacher not found")
    delete_obj(db, obj)


# ── Students ──────────────────────────────────────────────────────────────────
@router.get("/students/", response_model=List[StudentOut], tags=["Students"])
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                  _=Depends(get_current_user)):
    return get_all(db, Student, skip, limit)

@router.post("/students/", response_model=StudentOut, status_code=201, tags=["Students"])
def create_student(data: StudentCreate, db: Session = Depends(get_db),
                   _=Depends(require_teacher)):
    if db.query(Student).filter(Student.admission_number == data.admission_number).first():
        raise HTTPException(400, "Admission number already exists")
    return create_obj(db, Student, data.model_dump())

@router.get("/students/{id}", response_model=StudentOut, tags=["Students"])
def get_student(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, Student, id)
    if not obj: raise HTTPException(404, "Student not found")
    return obj

@router.put("/students/{id}", response_model=StudentOut, tags=["Students"])
def update_student(id: int, data: StudentUpdate, db: Session = Depends(get_db),
                   _=Depends(require_teacher)):
    obj = get_one(db, Student, id)
    if not obj: raise HTTPException(404, "Student not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/students/{id}", status_code=204, tags=["Students"])
def delete_student(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Student, id)
    if not obj: raise HTTPException(404, "Student not found")
    delete_obj(db, obj)


# ── Enrollments ───────────────────────────────────────────────────────────────
@router.get("/enrollments/", response_model=List[StudentCourseOut], tags=["Enrollments"])
def list_enrollments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                     _=Depends(get_current_user)):
    return get_all(db, StudentCourse, skip, limit)

@router.post("/enrollments/", response_model=StudentCourseOut, status_code=201, tags=["Enrollments"])
def create_enrollment(data: StudentCourseCreate, db: Session = Depends(get_db),
                      _=Depends(require_teacher)):
    return create_obj(db, StudentCourse, data.model_dump())

@router.get("/enrollments/{id}", response_model=StudentCourseOut, tags=["Enrollments"])
def get_enrollment(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, StudentCourse, id)
    if not obj: raise HTTPException(404, "Enrollment not found")
    return obj

@router.put("/enrollments/{id}", response_model=StudentCourseOut, tags=["Enrollments"])
def update_enrollment(id: int, data: StudentCourseUpdate, db: Session = Depends(get_db),
                      _=Depends(require_teacher)):
    obj = get_one(db, StudentCourse, id)
    if not obj: raise HTTPException(404, "Enrollment not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/enrollments/{id}", status_code=204, tags=["Enrollments"])
def delete_enrollment(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, StudentCourse, id)
    if not obj: raise HTTPException(404, "Enrollment not found")
    delete_obj(db, obj)


# ── Parents ───────────────────────────────────────────────────────────────────
@router.get("/parents/", response_model=List[ParentOut], tags=["Parents"])
def list_parents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                 _=Depends(get_current_user)):
    return get_all(db, Parent, skip, limit)

@router.post("/parents/", response_model=ParentOut, status_code=201, tags=["Parents"])
def create_parent(data: ParentCreate, db: Session = Depends(get_db),
                  _=Depends(require_admin)):
    return create_obj(db, Parent, data.model_dump())

@router.get("/parents/{id}", response_model=ParentOut, tags=["Parents"])
def get_parent(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, Parent, id)
    if not obj: raise HTTPException(404, "Parent not found")
    return obj

@router.put("/parents/{id}", response_model=ParentOut, tags=["Parents"])
def update_parent(id: int, data: ParentUpdate, db: Session = Depends(get_db),
                  _=Depends(require_admin)):
    obj = get_one(db, Parent, id)
    if not obj: raise HTTPException(404, "Parent not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/parents/{id}", status_code=204, tags=["Parents"])
def delete_parent(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Parent, id)
    if not obj: raise HTTPException(404, "Parent not found")
    delete_obj(db, obj)

@router.get("/parent-relationships/", response_model=List[ParentRelationshipOut], tags=["Parents"])
def list_relationships(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, ParentRelationship)

@router.post("/parent-relationships/", response_model=ParentRelationshipOut, status_code=201, tags=["Parents"])
def create_relationship(data: ParentRelationshipCreate, db: Session = Depends(get_db),
                        _=Depends(require_admin)):
    return create_obj(db, ParentRelationship, data.model_dump())
