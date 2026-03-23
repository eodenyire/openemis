"""Transportation module models"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    registration_number = Column(String(50), unique=True, nullable=False)
    capacity = Column(Integer)
    driver_name = Column(String(200))
    driver_phone = Column(String(20))
    active = Column(Boolean, default=True)
    routes = relationship("TransportRoute", back_populates="vehicle")


class TransportRoute(Base):
    __tablename__ = "transport_routes"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    start_point = Column(String(200))
    end_point = Column(String(200))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vehicle = relationship("Vehicle", back_populates="routes")
    stops = relationship("TransportRouteStop", back_populates="route",
                         order_by="TransportRouteStop.sequence", cascade="all, delete-orphan")
    student_assignments = relationship("StudentTransport", back_populates="route")


class TransportRouteStop(Base):
    __tablename__ = "transport_route_stops"
    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("transport_routes.id"), nullable=False)
    name = Column(String(200), nullable=False)
    sequence = Column(Integer, default=1)
    location = Column(String(255))
    pickup_time = Column(String(10))

    route = relationship("TransportRoute", back_populates="stops")


class StudentTransport(Base):
    __tablename__ = "student_transports"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("transport_routes.id"), nullable=False)
    stop_id = Column(Integer, ForeignKey("transport_route_stops.id"))
    transport_type = Column(String(20), default="both")   # both | to_school | from_school
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    route = relationship("TransportRoute", back_populates="student_assignments")
    stop = relationship("TransportRouteStop")
    academic_year = relationship("AcademicYear")
