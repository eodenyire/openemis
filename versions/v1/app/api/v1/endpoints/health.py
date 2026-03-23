"""
Health endpoints — student health records, clinic visits,
vaccination tracking, health summary.
"""
from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.health import (
    StudentHealth, MedicalCondition, Vaccination,
    ClinicVisit, VaccinationRecord, VisitType, VisitDisposition,
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class ConditionCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ConditionOut(BaseModel):
    id: int; name: str; description: Optional[str]
    class Config: from_attributes = True

class VaccinationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    doses_required: int = 1

class VaccinationOut(BaseModel):
    id: int; name: str; doses_required: int
    class Config: from_attributes = True

class HealthRecordCreate(BaseModel):
    student_id: int
    blood_group: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    allergies: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_number: Optional[str] = None
    notes: Optional[str] = None

class HealthRecordUpdate(BaseModel):
    blood_group: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    allergies: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_number: Optional[str] = None
    notes: Optional[str] = None
    last_checkup_date: Optional[date] = None

class HealthRecordOut(BaseModel):
    id: int; student_id: int; blood_group: Optional[str]
    height: Optional[float]; weight: Optional[float]; bmi: Optional[float]
    allergies: Optional[str]; emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]; doctor_name: Optional[str]
    insurance_provider: Optional[str]; last_checkup_date: Optional[date]
    class Config: from_attributes = True

class ClinicVisitCreate(BaseModel):
    student_id: int
    visit_date: date
    visit_type: str = "sick"
    complaint: str
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    medication_given: Optional[str] = None
    disposition: str = "treated_sent_back"
    referred_to: Optional[str] = None
    follow_up_date: Optional[date] = None
    attended_by: Optional[str] = None

class ClinicVisitOut(BaseModel):
    id: int; student_id: int; visit_date: date
    visit_type: str; complaint: str; diagnosis: Optional[str]
    treatment: Optional[str]; disposition: str
    attended_by: Optional[str]; follow_up_date: Optional[date]
    class Config: from_attributes = True

class VaccinationRecordCreate(BaseModel):
    student_id: int
    vaccination_id: int
    dose_number: int = 1
    date_given: date
    batch_number: Optional[str] = None
    administered_by: Optional[str] = None
    next_dose_date: Optional[date] = None
    notes: Optional[str] = None


# ── Reference data ────────────────────────────────────────────────────────────

@router.get("/conditions", response_model=List[ConditionOut])
def list_conditions(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(MedicalCondition).all()

@router.post("/conditions", response_model=ConditionOut, status_code=201)
def create_condition(data: ConditionCreate, db: Session = Depends(get_db),
                     _=Depends(require_admin)):
    if db.query(MedicalCondition).filter_by(name=data.name).first():
        raise HTTPException(409, "Condition already exists")
    obj = MedicalCondition(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/vaccinations", response_model=List[VaccinationOut])
def list_vaccinations(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Vaccination).all()

@router.post("/vaccinations", response_model=VaccinationOut, status_code=201)
def create_vaccination(data: VaccinationCreate, db: Session = Depends(get_db),
                       _=Depends(require_admin)):
    if db.query(Vaccination).filter_by(name=data.name).first():
        raise HTTPException(409, "Vaccination already exists")
    obj = Vaccination(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# ── Student Health Records ────────────────────────────────────────────────────

@router.get("/records", response_model=List[HealthRecordOut])
def list_records(skip: int = 0, limit: int = 100,
                 db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(StudentHealth).offset(skip).limit(limit).all()

@router.post("/records", response_model=HealthRecordOut, status_code=201)
def create_record(data: HealthRecordCreate, db: Session = Depends(get_db),
                  _=Depends(get_current_user)):
    if db.query(StudentHealth).filter_by(student_id=data.student_id).first():
        raise HTTPException(409, "Health record already exists for this student")
    payload = data.model_dump()
    # Compute BMI if height and weight provided
    if data.height and data.weight and data.height > 0:
        payload["bmi"] = round(data.weight / ((data.height / 100) ** 2), 1)
    obj = StudentHealth(**payload)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/records/{student_id}", response_model=HealthRecordOut)
def get_record(student_id: int, db: Session = Depends(get_db),
               _=Depends(get_current_user)):
    obj = db.query(StudentHealth).filter_by(student_id=student_id).first()
    if not obj: raise HTTPException(404, "Health record not found")
    return obj

@router.put("/records/{student_id}", response_model=HealthRecordOut)
def update_record(student_id: int, data: HealthRecordUpdate,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(StudentHealth).filter_by(student_id=student_id).first()
    if not obj: raise HTTPException(404, "Health record not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    if obj.height and obj.weight and obj.height > 0:
        obj.bmi = round(obj.weight / ((obj.height / 100) ** 2), 1)
    db.commit(); db.refresh(obj)
    return obj

@router.post("/records/{student_id}/conditions/{condition_id}")
def add_condition(student_id: int, condition_id: int,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    record = db.query(StudentHealth).filter_by(student_id=student_id).first()
    if not record: raise HTTPException(404, "Health record not found")
    condition = db.query(MedicalCondition).get(condition_id)
    if not condition: raise HTTPException(404, "Condition not found")
    if condition not in record.conditions:
        record.conditions.append(condition)
        db.commit()
    return {"student_id": student_id, "condition": condition.name}

@router.delete("/records/{student_id}/conditions/{condition_id}", status_code=204)
def remove_condition(student_id: int, condition_id: int,
                     db: Session = Depends(get_db), _=Depends(get_current_user)):
    record = db.query(StudentHealth).filter_by(student_id=student_id).first()
    if not record: raise HTTPException(404, "Health record not found")
    condition = db.query(MedicalCondition).get(condition_id)
    if condition and condition in record.conditions:
        record.conditions.remove(condition)
        db.commit()


# ── Clinic Visits ─────────────────────────────────────────────────────────────

@router.get("/visits", response_model=List[ClinicVisitOut])
def list_visits(skip: int = 0, limit: int = 100,
                student_id: Optional[int] = None,
                visit_type: Optional[str] = None,
                db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(ClinicVisit)
    if student_id: q = q.filter_by(student_id=student_id)
    if visit_type: q = q.filter(ClinicVisit.visit_type == visit_type)
    return q.order_by(ClinicVisit.visit_date.desc()).offset(skip).limit(limit).all()

@router.post("/visits", response_model=ClinicVisitOut, status_code=201)
def create_visit(data: ClinicVisitCreate, db: Session = Depends(get_db),
                 _=Depends(get_current_user)):
    record = db.query(StudentHealth).filter_by(student_id=data.student_id).first()
    if not record:
        raise HTTPException(404, "No health record for this student — create one first")
    visit = ClinicVisit(
        health_id=record.id,
        visit_type=VisitType(data.visit_type),
        disposition=VisitDisposition(data.disposition),
        **{k: v for k, v in data.model_dump().items()
           if k not in ("visit_type", "disposition")},
    )
    db.add(visit); db.commit(); db.refresh(visit)
    return visit

@router.get("/visits/{id}", response_model=ClinicVisitOut)
def get_visit(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(ClinicVisit).get(id)
    if not obj: raise HTTPException(404, "Visit not found")
    return obj

@router.put("/visits/{id}", response_model=ClinicVisitOut)
def update_visit(id: int, data: ClinicVisitCreate,
                 db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(ClinicVisit).get(id)
    if not obj: raise HTTPException(404, "Visit not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.get("/student/{student_id}/visits", response_model=List[ClinicVisitOut])
def student_visits(student_id: int, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
    return (db.query(ClinicVisit)
            .filter_by(student_id=student_id)
            .order_by(ClinicVisit.visit_date.desc()).all())


# ── Vaccination Records ───────────────────────────────────────────────────────

@router.post("/vaccination-records", status_code=201)
def record_vaccination(data: VaccinationRecordCreate,
                       db: Session = Depends(get_db), _=Depends(get_current_user)):
    record = db.query(StudentHealth).filter_by(student_id=data.student_id).first()
    if not record:
        raise HTTPException(404, "No health record for this student")
    obj = VaccinationRecord(health_id=record.id, **data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "student_id": obj.student_id,
            "vaccination_id": obj.vaccination_id, "date_given": obj.date_given}

@router.get("/student/{student_id}/vaccinations")
def student_vaccinations(student_id: int, db: Session = Depends(get_db),
                         _=Depends(get_current_user)):
    records = db.query(VaccinationRecord).filter_by(student_id=student_id).all()
    return [
        {"id": r.id, "vaccination": r.vaccination.name,
         "dose": r.dose_number, "date_given": r.date_given,
         "next_dose_date": r.next_dose_date, "administered_by": r.administered_by}
        for r in records
    ]


# ── Health summary ────────────────────────────────────────────────────────────

@router.get("/summary")
def health_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_records = db.query(StudentHealth).count()
    total_visits = db.query(ClinicVisit).count()
    visits_today = db.query(ClinicVisit).filter_by(visit_date=date.today()).count()
    referred = db.query(ClinicVisit).filter_by(
        disposition=VisitDisposition.REFERRED_HOSPITAL).count()
    sent_home = db.query(ClinicVisit).filter_by(
        disposition=VisitDisposition.SENT_HOME).count()

    # Visit type breakdown
    from sqlalchemy import func
    type_counts = (db.query(ClinicVisit.visit_type, func.count(ClinicVisit.id))
                   .group_by(ClinicVisit.visit_type).all())

    return {
        "students_with_health_records": total_records,
        "total_clinic_visits": total_visits,
        "visits_today": visits_today,
        "referred_to_hospital": referred,
        "sent_home": sent_home,
        "visits_by_type": {str(t): c for t, c in type_counts},
        "medical_conditions_tracked": db.query(MedicalCondition).count(),
        "vaccinations_tracked": db.query(Vaccination).count(),
    }
