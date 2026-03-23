"""User / auth model for v2."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SAEnum
from app.db.base import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"
    parent = "parent"
    staff = "staff"


class User(Base):
    __tablename__ = "op_users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(128), unique=True)
    hashed_password = Column(String(256), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.student)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
