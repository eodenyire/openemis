"""
Transport v2 — enhanced: route manifest, student lookup by route,
vehicle capacity tracking, transport summary, GPS-ready tracking stub.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.transportation import (
    Vehicle, TransportRoute, TransportRouteStop, StudentTransport,
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class AssignRequest(BaseModel):
    student_id: int
    route_id: int
    stop_id: Optional[int] = None
    transport_type: str = "both"   # both | to_school | from_school
    academic_year_id: Optional[int] = None

class AssignOut(BaseModel):
    id: int; student_id: int; route_id: int
    stop_id: Optional[int]; transport_type: str; active: bool
    class Config: from_attributes = True

class VehicleOut(BaseModel):
    id: int; name: str; registration_number: str
    capacity: Optional[int]; driver_name: Optional[str]
    driver_phone: Optional[str]; active: bool
    class Config: from_attributes = True


# ── Route manifest ────────────────────────────────────────────────────────────

@router.get("/routes/{route_id}/manifest")
def route_manifest(route_id: int, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
    """Full manifest: route info, stops in order, students per stop."""
    route = db.query(TransportRoute).get(route_id)
    if not route: raise HTTPException(404, "Route not found")

    vehicle = db.query(Vehicle).get(route.vehicle_id) if route.vehicle_id else None
    stops = (db.query(TransportRouteStop)
             .filter_by(route_id=route_id)
             .order_by(TransportRouteStop.sequence).all())

    stop_data = []
    for stop in stops:
        students = db.query(StudentTransport).filter_by(
            route_id=route_id, stop_id=stop.id, active=True).all()
        stop_data.append({
            "stop_id": stop.id,
            "name": stop.name,
            "sequence": stop.sequence,
            "pickup_time": stop.pickup_time,
            "location": stop.location,
            "student_count": len(students),
            "students": [{"student_id": s.student_id,
                          "transport_type": s.transport_type} for s in students],
        })

    total_students = db.query(StudentTransport).filter_by(
        route_id=route_id, active=True).count()
    capacity = vehicle.capacity if vehicle else None

    return {
        "route_id": route.id,
        "route_name": route.name,
        "start_point": route.start_point,
        "end_point": route.end_point,
        "vehicle": {
            "id": vehicle.id if vehicle else None,
            "name": vehicle.name if vehicle else None,
            "registration": vehicle.registration_number if vehicle else None,
            "capacity": capacity,
            "driver": vehicle.driver_name if vehicle else None,
            "driver_phone": vehicle.driver_phone if vehicle else None,
        },
        "total_students": total_students,
        "capacity_used": f"{total_students}/{capacity}" if capacity else str(total_students),
        "stops": stop_data,
    }


# ── Student transport lookup ──────────────────────────────────────────────────

@router.get("/student/{student_id}")
def student_transport(student_id: int, db: Session = Depends(get_db),
                      _=Depends(get_current_user)):
    assignments = db.query(StudentTransport).filter_by(
        student_id=student_id, active=True).all()
    if not assignments:
        raise HTTPException(404, "No active transport assignment for this student")
    result = []
    for a in assignments:
        route = db.query(TransportRoute).get(a.route_id)
        stop = db.query(TransportRouteStop).get(a.stop_id) if a.stop_id else None
        vehicle = db.query(Vehicle).get(route.vehicle_id) if route and route.vehicle_id else None
        result.append({
            "assignment_id": a.id,
            "route": route.name if route else None,
            "stop": stop.name if stop else None,
            "pickup_time": stop.pickup_time if stop else None,
            "transport_type": a.transport_type,
            "vehicle": vehicle.name if vehicle else None,
            "driver": vehicle.driver_name if vehicle else None,
            "driver_phone": vehicle.driver_phone if vehicle else None,
        })
    return result


@router.post("/assign", response_model=AssignOut, status_code=201)
def assign_student(data: AssignRequest, db: Session = Depends(get_db),
                   _=Depends(require_admin)):
    route = db.query(TransportRoute).get(data.route_id)
    if not route: raise HTTPException(404, "Route not found")

    # Check vehicle capacity
    if route.vehicle_id:
        vehicle = db.query(Vehicle).get(route.vehicle_id)
        if vehicle and vehicle.capacity:
            current = db.query(StudentTransport).filter_by(
                route_id=data.route_id, active=True).count()
            if current >= vehicle.capacity:
                raise HTTPException(400, f"Vehicle at full capacity ({vehicle.capacity})")

    # Check not already assigned to this route
    existing = db.query(StudentTransport).filter_by(
        student_id=data.student_id, route_id=data.route_id, active=True).first()
    if existing:
        raise HTTPException(409, "Student already assigned to this route")

    obj = StudentTransport(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.delete("/assign/{id}", status_code=204)
def unassign_student(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(StudentTransport).get(id)
    if not obj: raise HTTPException(404, "Assignment not found")
    obj.active = False
    db.commit()


# ── Vehicle utilization ───────────────────────────────────────────────────────

@router.get("/vehicles/utilization")
def vehicle_utilization(db: Session = Depends(get_db), _=Depends(get_current_user)):
    vehicles = db.query(Vehicle).filter_by(active=True).all()
    result = []
    for v in vehicles:
        routes = db.query(TransportRoute).filter_by(vehicle_id=v.id, active=True).all()
        total_students = sum(
            db.query(StudentTransport).filter_by(route_id=r.id, active=True).count()
            for r in routes
        )
        result.append({
            "vehicle_id": v.id,
            "name": v.name,
            "registration": v.registration_number,
            "capacity": v.capacity,
            "students_assigned": total_students,
            "utilization": round(total_students / v.capacity * 100, 1) if v.capacity else 0,
            "routes": [r.name for r in routes],
        })
    return result


# ── Transport summary ─────────────────────────────────────────────────────────

@router.get("/summary")
def transport_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_vehicles = db.query(Vehicle).filter_by(active=True).count()
    total_routes = db.query(TransportRoute).filter_by(active=True).count()
    total_stops = db.query(TransportRouteStop).count()
    total_students = db.query(StudentTransport).filter_by(active=True).count()
    total_capacity = sum(
        v.capacity or 0 for v in db.query(Vehicle).filter_by(active=True).all()
    )
    return {
        "total_vehicles": total_vehicles,
        "total_routes": total_routes,
        "total_stops": total_stops,
        "students_using_transport": total_students,
        "total_vehicle_capacity": total_capacity,
        "utilization_rate": round(total_students / total_capacity * 100, 1) if total_capacity else 0,
    }
