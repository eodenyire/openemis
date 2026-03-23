"""Transport endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.support import OpTransportRoute, OpVehicle, OpStudentTransport

router = APIRouter()


@router.get("/transport/routes")
def list_routes(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OpTransportRoute).filter_by(active=True).all()

@router.post("/transport/routes", status_code=201)
def create_route(name: str, start_point: Optional[str] = None, end_point: Optional[str] = None,
                 fare: float = 0, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpTransportRoute(name=name, start_point=start_point, end_point=end_point, fare=fare)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/transport/routes/{id}")
def get_route(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpTransportRoute).get(id)
    if not obj: raise HTTPException(404, "Route not found")
    return obj


@router.get("/transport/vehicles")
def list_vehicles(route_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpVehicle).filter_by(active=True)
    if route_id: q = q.filter_by(route_id=route_id)
    return q.all()

@router.post("/transport/vehicles", status_code=201)
def create_vehicle(name: str, registration_number: str, capacity: Optional[int] = None,
                   driver_name: Optional[str] = None, driver_phone: Optional[str] = None,
                   route_id: Optional[int] = None,
                   db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpVehicle(name=name, registration_number=registration_number, capacity=capacity,
                    driver_name=driver_name, driver_phone=driver_phone, route_id=route_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj


@router.get("/transport/student-assignments")
def list_student_transport(student_id: Optional[int] = None, route_id: Optional[int] = None,
                            db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpStudentTransport).filter_by(active=True)
    if student_id: q = q.filter_by(student_id=student_id)
    if route_id: q = q.filter_by(route_id=route_id)
    return q.all()

@router.post("/transport/student-assignments", status_code=201)
def assign_student(student_id: int, route_id: int, academic_year_id: Optional[int] = None,
                   db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpStudentTransport(student_id=student_id, route_id=route_id, academic_year_id=academic_year_id)
    db.add(obj); db.commit(); db.refresh(obj); return obj
