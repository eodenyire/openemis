from pydantic import BaseModel
from typing import Optional


class VehicleBase(BaseModel):
    name: str
    registration_number: str
    capacity: Optional[int] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
class VehicleCreate(VehicleBase): pass
class VehicleUpdate(BaseModel):
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
class VehicleOut(VehicleBase):
    id: int
    class Config: from_attributes = True

class RouteStopBase(BaseModel):
    name: str
    sequence: Optional[int] = 1
    location: Optional[str] = None
    pickup_time: Optional[str] = None
class RouteStopCreate(RouteStopBase): pass
class RouteStopOut(RouteStopBase):
    id: int
    class Config: from_attributes = True

class TransportRouteBase(BaseModel):
    name: str
    vehicle_id: Optional[int] = None
    start_point: Optional[str] = None
    end_point: Optional[str] = None
class TransportRouteCreate(TransportRouteBase): pass
class TransportRouteUpdate(BaseModel):
    name: Optional[str] = None
    vehicle_id: Optional[int] = None
class TransportRouteOut(TransportRouteBase):
    id: int
    class Config: from_attributes = True

class StudentTransportBase(BaseModel):
    student_id: int
    route_id: int
    stop_id: Optional[int] = None
    transport_type: Optional[str] = "both"
    academic_year_id: Optional[int] = None
class StudentTransportCreate(StudentTransportBase): pass
class StudentTransportUpdate(BaseModel):
    route_id: Optional[int] = None
    stop_id: Optional[int] = None
    transport_type: Optional[str] = None
class StudentTransportOut(StudentTransportBase):
    id: int
    class Config: from_attributes = True
