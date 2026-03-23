"""Support service models — hostel, library, health, transport, cafeteria, inventory."""
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


# ── Library ───────────────────────────────────────────────────────────────────

class OpLibraryBook(Base):
    __tablename__ = "op_library_books"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    isbn = Column(String(32), unique=True)
    author = Column(String(128))
    publisher = Column(String(128))
    edition = Column(String(32))
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    category = Column(String(64))
    active = Column(Boolean, default=True)
    movements = relationship("OpLibraryMovement", back_populates="book")


class OpLibraryMovement(Base):
    __tablename__ = "op_library_movements"
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("op_library_books.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date)
    return_date = Column(Date)
    state = Column(String(16), default="issued")  # issued | returned | overdue
    note = Column(Text)
    book = relationship("OpLibraryBook", back_populates="movements")
    student = relationship("OpStudent")


# ── Hostel ────────────────────────────────────────────────────────────────────

class OpHostelBlock(Base):
    __tablename__ = "op_hostel_blocks"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    code = Column(String(16), nullable=False, unique=True)
    capacity = Column(Integer, default=0)
    description = Column(Text)
    active = Column(Boolean, default=True)
    rooms = relationship("OpHostelRoom", back_populates="block")


class OpHostelRoomType(Base):
    __tablename__ = "op_hostel_room_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    capacity = Column(Integer, nullable=False)
    monthly_fee = Column(Float, default=0.0)
    description = Column(Text)
    active = Column(Boolean, default=True)


class OpHostelRoom(Base):
    __tablename__ = "op_hostel_rooms"
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    block_id = Column(Integer, ForeignKey("op_hostel_blocks.id"), nullable=False)
    room_type_id = Column(Integer, ForeignKey("op_hostel_room_types.id"), nullable=False)
    capacity = Column(Integer, default=0)
    occupied = Column(Integer, default=0)
    available = Column(Integer, default=0)
    state = Column(String(24), default="available")  # available, partially_occupied, fully_occupied, maintenance
    description = Column(Text)
    active = Column(Boolean, default=True)
    block = relationship("OpHostelBlock", back_populates="rooms")
    room_type = relationship("OpHostelRoomType")
    allocations = relationship("OpHostelAllocation", back_populates="room")


class OpHostelAllocation(Base):
    __tablename__ = "op_hostel_allocations"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("op_hostel_rooms.id"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("op_academic_years.id"))
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date)
    monthly_fee = Column(Float, default=0.0)
    state = Column(String(16), default="draft")  # draft, confirmed, checked_out, cancelled
    notes = Column(Text)
    active = Column(Boolean, default=True)
    student = relationship("OpStudent")
    room = relationship("OpHostelRoom", back_populates="allocations")


# ── Health ────────────────────────────────────────────────────────────────────

class OpHealthRecord(Base):
    __tablename__ = "op_health_records"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    visit_date = Column(Date, nullable=False)
    complaint = Column(Text)
    diagnosis = Column(Text)
    treatment = Column(Text)
    doctor = Column(String(128))
    follow_up_date = Column(Date)
    active = Column(Boolean, default=True)
    student = relationship("OpStudent")


# ── Transport ─────────────────────────────────────────────────────────────────

class OpTransportVehicle(Base):
    __tablename__ = "op_transport_vehicles"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    registration_number = Column(String(32), nullable=False, unique=True)
    vehicle_type = Column(String(16), default="bus")  # bus, van, minibus, car
    capacity = Column(Integer, default=0)
    driver_name = Column(String(128))
    driver_phone = Column(String(20))
    driver_license = Column(String(64))
    notes = Column(Text)
    active = Column(Boolean, default=True)
    routes = relationship("OpTransportRoute", back_populates="vehicle")


class OpTransportRoute(Base):
    __tablename__ = "op_transport_routes"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    code = Column(String(16), nullable=False, unique=True)
    vehicle_id = Column(Integer, ForeignKey("op_transport_vehicles.id"))
    departure_time = Column(Float, default=0.0)
    return_time = Column(Float, default=0.0)
    active = Column(Boolean, default=True)
    vehicle = relationship("OpTransportVehicle", back_populates="routes")
    stops = relationship("OpTransportRouteStop", back_populates="route")


class OpTransportRouteStop(Base):
    __tablename__ = "op_transport_route_stops"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    route_id = Column(Integer, ForeignKey("op_transport_routes.id"), nullable=False)
    sequence = Column(Integer, default=10)
    arrival_time = Column(Float, default=0.0)
    landmark = Column(String(256))
    active = Column(Boolean, default=True)
    route = relationship("OpTransportRoute", back_populates="stops")


class OpStudentTransport(Base):
    __tablename__ = "op_student_transports"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("op_transport_routes.id"), nullable=False)
    stop_id = Column(Integer, ForeignKey("op_transport_route_stops.id"))
    transport_type = Column(String(16), default="both")  # both, to_school, from_school
    academic_year_id = Column(Integer, ForeignKey("op_academic_years.id"))
    active = Column(Boolean, default=True)
    student = relationship("OpStudent")
    route = relationship("OpTransportRoute")
