"""HR endpoints — Staff profiles, employment management."""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.hr import (
    StaffProfile, EmploymentType, EmploymentStatus,
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class StaffCreate(BaseModel):
    user_id: int
    teacher_id: Optional[int] = None
    tsc_number: Optional[str] = None
    national_id: Optional[str] = None
    kra_pin: Optional[str] = None
    nhif_number: Optional[str] = None
    nssf_number: Optional[str] = None
    employment_type: str = "permanent"
    job_title: Optional[str] = None
    department_id: Optional[int] = None
    reporting_to_id: Optional[int] = None
    hire_date: date
    basic_salary: float = 0
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None

class StaffUpdate(BaseModel):
    job_title: Optional[str] = None
    department_id: Optional[int] = None
    employment_type: Optional[str] = None
    employment_status: Optional[str] = None
    basic_salary: Optional[float] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    tsc_number: Optional[str] = None
    kra_pin: Optional[str] = None
    nhif_number: Optional[str] = None
    nssf_number: Optional[str] = None
    reporting_to_id: Optional[int] = None

class StaffOut(BaseModel):
    id: int
    user_id: int
    teacher_id: Optional[int]
    tsc_number: Optional[str]
    national_id: Optional[str]
    kra_pin: Optional[str]
    nhif_number: Optional[str]
    nssf_number: Optional[str]
    employment_type: str
    employment_status: str
    job_title: Optional[str]
    department_id: Optional[int]
    hire_date: date
    basic_salary: Optional[Decimal]
    bank_name: Optional[str]
    class Config: from_attributes = True


# ── Staff CRUD ────────────────────────────────────────────────────────────────

@router.get("/staff", response_model=List[StaffOut])
def list_staff(skip: int = 0, limit: int = 100,
               status: Optional[str] = None,
               department_id: Optional[int] = None,
               db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(StaffProfile)
    if status:
        q = q.filter(StaffProfile.employment_status == status)
    if department_id:
        q = q.filter_by(department_id=department_id)
    return q.offset(skip).limit(limit).all()

@router.post("/staff", response_model=StaffOut, status_code=201)
def create_staff(data: StaffCreate, db: Session = Depends(get_db),
                 _=Depends(require_admin)):
    if db.query(StaffProfile).filter_by(user_id=data.user_id).first():
        raise HTTPException(409, "Staff profile already exists for this user")
    obj = StaffProfile(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/staff/{id}", response_model=StaffOut)
def get_staff(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(StaffProfile).get(id)
    if not obj: raise HTTPException(404, "Staff profile not found")
    return obj

@router.put("/staff/{id}", response_model=StaffOut)
def update_staff(id: int, data: StaffUpdate, db: Session = Depends(get_db),
                 _=Depends(require_admin)):
    obj = db.query(StaffProfile).get(id)
    if not obj: raise HTTPException(404, "Staff profile not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/staff/{id}", status_code=204)
def delete_staff(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(StaffProfile).get(id)
    if not obj: raise HTTPException(404, "Staff profile not found")
    db.delete(obj); db.commit()

@router.put("/staff/{id}/terminate")
def terminate_staff(id: int, reason: str, termination_date: date,
                    db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(StaffProfile).get(id)
    if not obj: raise HTTPException(404, "Staff profile not found")
    obj.employment_status = EmploymentStatus.TERMINATED
    obj.termination_date = termination_date
    obj.termination_reason = reason
    db.commit()
    return {"id": obj.id, "status": obj.employment_status}

@router.get("/staff/by-user/{user_id}", response_model=StaffOut)
def get_staff_by_user(user_id: int, db: Session = Depends(get_db),
                      _=Depends(get_current_user)):
    obj = db.query(StaffProfile).filter_by(user_id=user_id).first()
    if not obj: raise HTTPException(404, "Staff profile not found")
    return obj

@router.get("/staff/{id}/direct-reports", response_model=List[StaffOut])
def get_direct_reports(id: int, db: Session = Depends(get_db),
                       _=Depends(get_current_user)):
    return db.query(StaffProfile).filter_by(reporting_to_id=id).all()
