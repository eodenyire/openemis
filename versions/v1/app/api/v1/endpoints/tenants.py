"""Tenant (school) management endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.api.deps import require_admin
from app.models.tenant import Tenant, TenantGroup, SchoolType, SubscriptionPlan

router = APIRouter()


class TenantCreate(BaseModel):
    name: str
    slug: str
    school_type: SchoolType = SchoolType.PUBLIC
    subscription_plan: SubscriptionPlan = SubscriptionPlan.BASIC
    county: Optional[str] = None
    sub_county: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    nemis_code: Optional[str] = None
    group_id: Optional[int] = None


class TenantGroupCreate(BaseModel):
    name: str
    code: str
    county: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


@router.get("/")
def list_tenants(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(Tenant).filter(Tenant.is_active == True).all()


@router.post("/")
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    existing = db.query(Tenant).filter(Tenant.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already taken")
    tenant = Tenant(**payload.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("/{tenant_id}")
def get_tenant(tenant_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return t


@router.get("/groups/")
def list_groups(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(TenantGroup).all()


@router.post("/groups/")
def create_group(payload: TenantGroupCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    g = TenantGroup(**payload.model_dump())
    db.add(g)
    db.commit()
    db.refresh(g)
    return g
