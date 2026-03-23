"""Facilities endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.extras import OpFacility

router = APIRouter()


@router.get("/facilities")
def list_facilities(facility_type: Optional[str] = None, state: Optional[str] = None,
                    db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpFacility).filter_by(active=True)
    if facility_type: q = q.filter_by(facility_type=facility_type)
    if state: q = q.filter_by(state=state)
    return q.all()

@router.post("/facilities", status_code=201)
def create_facility(name: str, facility_type: Optional[str] = None,
                    capacity: Optional[int] = None, location: Optional[str] = None,
                    db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpFacility(name=name, facility_type=facility_type, capacity=capacity, location=location)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/facilities/{id}")
def get_facility(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpFacility).get(id)
    if not obj: raise HTTPException(404, "Facility not found")
    return obj

@router.patch("/facilities/{id}/state")
def update_facility_state(id: int, state: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpFacility).get(id)
    if not obj: raise HTTPException(404, "Facility not found")
    obj.state = state
    db.commit(); db.refresh(obj); return obj

@router.delete("/facilities/{id}", status_code=204)
def delete_facility(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpFacility).get(id)
    if not obj: raise HTTPException(404, "Facility not found")
    obj.active = False; db.commit()
