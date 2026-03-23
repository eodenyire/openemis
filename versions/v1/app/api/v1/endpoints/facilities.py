"""Facilities management endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.extras import Facility

router = APIRouter()


class FacilityCreate(BaseModel):
    name: str
    facility_type: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    description: Optional[str] = None

class FacilityUpdate(BaseModel):
    name: Optional[str] = None
    facility_type: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    description: Optional[str] = None
    active: Optional[bool] = None


@router.get("/")
def list_facilities(
    facility_type: Optional[str] = None,
    active_only: bool = True,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(Facility)
    if active_only: q = q.filter_by(active=True)
    if facility_type: q = q.filter_by(facility_type=facility_type)
    total = q.count()
    items = q.order_by(Facility.name).offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": f.id, "name": f.name, "facility_type": f.facility_type,
         "location": f.location, "capacity": f.capacity, "active": f.active}
        for f in items
    ]}

@router.post("/", status_code=201)
def create_facility(data: FacilityCreate, db: Session = Depends(get_db),
                    _=Depends(get_current_user)):
    obj = Facility(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "name": obj.name}

@router.get("/{id}")
def get_facility(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Facility).filter_by(id=id).first()
    if not obj: raise HTTPException(404, "Facility not found")
    return {"id": obj.id, "name": obj.name, "facility_type": obj.facility_type,
            "location": obj.location, "capacity": obj.capacity,
            "description": obj.description, "active": obj.active}

@router.put("/{id}")
def update_facility(id: int, data: FacilityUpdate, db: Session = Depends(get_db),
                    _=Depends(get_current_user)):
    obj = db.query(Facility).filter_by(id=id).first()
    if not obj: raise HTTPException(404, "Facility not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "name": obj.name}

@router.delete("/{id}", status_code=204)
def delete_facility(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Facility).filter_by(id=id).first()
    if not obj: raise HTTPException(404, "Facility not found")
    obj.active = False; db.commit()
