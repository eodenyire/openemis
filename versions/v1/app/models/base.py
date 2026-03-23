"""
Base model mixins and utilities
"""
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.sql import func


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ActiveMixin:
    """Mixin for soft delete functionality"""
    active = Column(Boolean, default=True, nullable=False)


class BaseModel(TimestampMixin, ActiveMixin):
    """Base model with common fields"""
    pass
