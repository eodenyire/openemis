import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class UserRole(str, enum.Enum):
    # Legacy roles (kept for backward compat)
    ADMIN = "admin"
    STAFF = "staff"
    # 15 CBC EMIS roles
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    ACADEMIC_DIRECTOR = "academic_director"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"
    FINANCE_OFFICER = "finance_officer"
    REGISTRAR = "registrar"
    LIBRARIAN = "librarian"
    TRANSPORT_MANAGER = "transport_manager"
    HR_MANAGER = "hr_manager"
    NURSE = "nurse"
    HOSTEL_MANAGER = "hostel_manager"
    SECURITY_OFFICER = "security_officer"
    GOVERNMENT = "government"

    @classmethod
    def cbc_roles(cls) -> list:
        """Return the 15 CBC EMIS roles (excludes legacy)."""
        return [
            cls.SUPER_ADMIN, cls.SCHOOL_ADMIN, cls.ACADEMIC_DIRECTOR,
            cls.TEACHER, cls.STUDENT, cls.PARENT, cls.FINANCE_OFFICER,
            cls.REGISTRAR, cls.LIBRARIAN, cls.TRANSPORT_MANAGER,
            cls.HR_MANAGER, cls.NURSE, cls.HOSTEL_MANAGER,
            cls.SECURITY_OFFICER, cls.GOVERNMENT,
        ]


class Permission(Base):
    """resource:action:scope  e.g. students:read:class  students:write:school"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(120), unique=True, nullable=False, index=True)
    description = Column(String(255))
    resource = Column(String(60), nullable=False)
    action = Column(String(30), nullable=False)   # read / write / delete / approve
    scope = Column(String(30), nullable=False)     # own / class / school / system

    role_permissions = relationship("RolePermission", back_populates="permission")


class RolePermission(Base):
    """Maps a UserRole enum value to a Permission."""
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(30), nullable=False, index=True)  # store as plain string matching enum value
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)

    permission = relationship("Permission", back_populates="role_permissions")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    # Refresh token support
    refresh_token = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
