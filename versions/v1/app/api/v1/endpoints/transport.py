from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.api.crud import get_one, get_all, create_obj, update_obj, delete_obj
from app.models.transportation import Vehicle, TransportRoute, TransportRouteStop, StudentTransport
from app.schemas.transportation import (
    VehicleCreate, VehicleUpdate, VehicleOut,
    TransportRouteCreate, TransportRouteUpdate, TransportRouteOut,
    RouteStopCreate, RouteStopOut,
    StudentTransportCreate, StudentTransportUpdate, StudentTransportOut,
)

router = APIRouter()

@router.get("/vehicles", response_model=List[VehicleOut], tags=["Transport"])
def list_vehicles(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, Vehicle)

@router.post("/vehicles", response_model=VehicleOut, status_code=201, tags=["Transport"])
def create_vehicle(data: VehicleCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, Vehicle, data.model_dump())

@router.put("/vehicles/{id}", response_model=VehicleOut, tags=["Transport"])
def update_vehicle(id: int, data: VehicleUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Vehicle, id)
    if not obj: raise HTTPException(404, "Vehicle not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/vehicles/{id}", status_code=204, tags=["Transport"])
def delete_vehicle(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Vehicle, id)
    if not obj: raise HTTPException(404, "Vehicle not found")
    delete_obj(db, obj)

@router.get("/routes", response_model=List[TransportRouteOut], tags=["Transport"])
def list_routes(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, TransportRoute)

@router.post("/routes", response_model=TransportRouteOut, status_code=201, tags=["Transport"])
def create_route(data: TransportRouteCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, TransportRoute, data.model_dump())

@router.put("/routes/{id}", response_model=TransportRouteOut, tags=["Transport"])
def update_route(id: int, data: TransportRouteUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, TransportRoute, id)
    if not obj: raise HTTPException(404, "Route not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/routes/{id}", status_code=204, tags=["Transport"])
def delete_route(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, TransportRoute, id)
    if not obj: raise HTTPException(404, "Route not found")
    delete_obj(db, obj)

@router.get("/routes/{route_id}/stops", response_model=List[RouteStopOut], tags=["Transport"])
def list_stops(route_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(TransportRouteStop).filter(TransportRouteStop.route_id == route_id).order_by(TransportRouteStop.sequence).all()

@router.post("/routes/{route_id}/stops", response_model=RouteStopOut, status_code=201, tags=["Transport"])
def add_stop(route_id: int, data: RouteStopCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, TransportRouteStop, {**data.model_dump(), "route_id": route_id})

@router.delete("/stops/{id}", status_code=204, tags=["Transport"])
def delete_stop(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, TransportRouteStop, id)
    if not obj: raise HTTPException(404, "Stop not found")
    delete_obj(db, obj)

@router.get("/assignments", response_model=List[StudentTransportOut], tags=["Transport"])
def list_assignments(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, StudentTransport)

@router.post("/assignments", response_model=StudentTransportOut, status_code=201, tags=["Transport"])
def assign_student(data: StudentTransportCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, StudentTransport, data.model_dump())

@router.put("/assignments/{id}", response_model=StudentTransportOut, tags=["Transport"])
def update_assignment(id: int, data: StudentTransportUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, StudentTransport, id)
    if not obj: raise HTTPException(404, "Assignment not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/assignments/{id}", status_code=204, tags=["Transport"])
def delete_assignment(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, StudentTransport, id)
    if not obj: raise HTTPException(404, "Assignment not found")
    delete_obj(db, obj)
