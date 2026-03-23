"""Hostel module models"""
import enum
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class HostelAllocationState(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"


class HostelBlock(Base):
    __tablename__ = "hostel_blocks"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    capacity = Column(Integer)
    active = Column(Boolean, default=True)
    rooms = relationship("HostelRoom", back_populates="block")


class HostelRoomType(Base):
    __tablename__ = "hostel_room_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    monthly_fee = Column(Float, nullable=False)
    capacity = Column(Integer, default=1)
    active = Column(Boolean, default=True)
    rooms = relationship("HostelRoom", back_populates="room_type")


class HostelRoom(Base):
    __tablename__ = "hostel_rooms"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    block_id = Column(Integer, ForeignKey("hostel_blocks.id"))
    room_type_id = Column(Integer, ForeignKey("hostel_room_types.id"))
    capacity = Column(Integer, nullable=False)
    state = Column(String(20), default="available")   # available | occupied | maintenance
    active = Column(Boolean, default=True)

    block = relationship("HostelBlock", back_populates="rooms")
    room_type = relationship("HostelRoomType", back_populates="rooms")
    allocations = relationship("HostelAllocation", back_populates="room")


class HostelAllocation(Base):
    __tablename__ = "hostel_allocations"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("hostel_rooms.id"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date)
    monthly_fee = Column(Float)
    state = Column(Enum(HostelAllocationState), default=HostelAllocationState.DRAFT)
    notes = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    room = relationship("HostelRoom", back_populates="allocations")
    academic_year = relationship("AcademicYear")
