from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import random, string
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin, require_teacher
from app.api.crud import get_one, get_all, create_obj, update_obj, delete_obj
from app.models.admission import Admission, AdmissionRegister
from app.schemas.admission import (
    AdmissionCreate, AdmissionUpdate, AdmissionOut,
    AdmissionRegisterCreate, AdmissionRegisterUpdate, AdmissionRegisterOut,
)

router = APIRouter()


def _gen_app_number():
    return "APP-" + "".join(random.choices(string.digits, k=8))


# ── Admission Registers ───────────────────────────────────────────────────────
@router.get("/registers/", response_model=List[AdmissionRegisterOut], tags=["Admission"])
def list_registers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
    return get_all(db, AdmissionRegister, skip, limit)

@router.post("/registers/", response_model=AdmissionRegisterOut, status_code=201, tags=["Admission"])
def create_register(data: AdmissionRegisterCreate, db: Session = Depends(get_db),
                    _=Depends(require_admin)):
    return create_obj(db, AdmissionRegister, data.model_dump())

@router.get("/registers/{id}", response_model=AdmissionRegisterOut, tags=["Admission"])
def get_register(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, AdmissionRegister, id)
    if not obj: raise HTTPException(404, "Register not found")
    return obj

@router.put("/registers/{id}", response_model=AdmissionRegisterOut, tags=["Admission"])
def update_register(id: int, data: AdmissionRegisterUpdate, db: Session = Depends(get_db),
                    _=Depends(require_admin)):
    obj = get_one(db, AdmissionRegister, id)
    if not obj: raise HTTPException(404, "Register not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/registers/{id}", status_code=204, tags=["Admission"])
def delete_register(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, AdmissionRegister, id)
    if not obj: raise HTTPException(404, "Register not found")
    delete_obj(db, obj)


# ── Admissions ────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[AdmissionOut], tags=["Admission"])
def list_admissions(skip: int = 0, limit: int = 100, state: str = None,
                    db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(Admission)
    if state:
        q = q.filter(Admission.state == state)
    return q.offset(skip).limit(limit).all()

@router.post("/", response_model=AdmissionOut, status_code=201, tags=["Admission"])
def create_admission(data: AdmissionCreate, db: Session = Depends(get_db),
                     _=Depends(get_current_user)):
    payload = data.model_dump()
    payload["application_number"] = _gen_app_number()
    payload["application_date"] = datetime.utcnow()
    payload["name"] = f"{data.first_name} {data.last_name}"
    return create_obj(db, Admission, payload)

@router.get("/{id}", response_model=AdmissionOut, tags=["Admission"])
def get_admission(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, Admission, id)
    if not obj: raise HTTPException(404, "Admission not found")
    return obj

@router.put("/{id}", response_model=AdmissionOut, tags=["Admission"])
def update_admission(id: int, data: AdmissionUpdate, db: Session = Depends(get_db),
                     _=Depends(require_teacher)):
    obj = get_one(db, Admission, id)
    if not obj: raise HTTPException(404, "Admission not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.post("/{id}/confirm", response_model=AdmissionOut, tags=["Admission"])
def confirm_admission(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Admission, id)
    if not obj: raise HTTPException(404, "Admission not found")
    return update_obj(db, obj, {"state": "confirm"})

@router.post("/{id}/approve", response_model=AdmissionOut, tags=["Admission"])
def approve_admission(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Admission, id)
    if not obj: raise HTTPException(404, "Admission not found")
    return update_obj(db, obj, {"state": "admission"})

@router.post("/{id}/reject", response_model=AdmissionOut, tags=["Admission"])
def reject_admission(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Admission, id)
    if not obj: raise HTTPException(404, "Admission not found")
    return update_obj(db, obj, {"state": "reject"})

@router.delete("/{id}", status_code=204, tags=["Admission"])
def delete_admission(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Admission, id)
    if not obj: raise HTTPException(404, "Admission not found")
    delete_obj(db, obj)
