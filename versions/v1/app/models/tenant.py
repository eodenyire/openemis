"""Multi-Tenancy models — Tenant (school) and TenantGroup (school network)."""
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


class SchoolType(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INTERNATIONAL = "international"
    SPECIAL_NEEDS = "special_needs"


class TenantGroup(Base):
    """A school network or county cluster that owns multiple schools."""
    __tablename__ = "tenant_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(30), unique=True, nullable=False)
    county = Column(String(100))
    contact_email = Column(String(200))
    contact_phone = Column(String(30))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenants = relationship("Tenant", back_populates="group")


class Tenant(Base):
    """A school registered on the platform."""
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(60), unique=True, nullable=False, index=True)
    school_type = Column(Enum(SchoolType), default=SchoolType.PUBLIC)
    subscription_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.BASIC)
    group_id = Column(Integer, ForeignKey("tenant_groups.id"), nullable=True)

    # Location
    county = Column(String(100))
    sub_county = Column(String(100))
    ward = Column(String(100))
    address = Column(Text)

    # Contact
    email = Column(String(200))
    phone = Column(String(30))
    website = Column(String(200))

    # NEMIS
    nemis_code = Column(String(30), nullable=True)

    # Branding
    logo_url = Column(String(500))
    primary_color = Column(String(10), default="#1a73e8")

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    group = relationship("TenantGroup", back_populates="tenants")
