"""Leave management endpoints — policies, balances, requests, approvals."""
from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.hr import (
    LeavePolicy, LeaveBalance, LeaveRequest,
    LeaveType, LeaveStatus, StaffProfile,
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class PolicyCreate(BaseModel):
    leave_type: str
    days_per_year: float
    carry_forward: bool = False
    max_carry_forward_days: float = 0
    requires_approval: bool = True
    description: Optional[str] = None

class PolicyOut(BaseModel):
    id: int; leave_type: str; days_per_year: float
    carry_forward: bool; max_carry_forward_days: float
    class Config: from_attributes = True

class BalanceOut(BaseModel):
    id: int; staff_id: int; leave_type: str
    entitled_days: float; used_days: float; carried_forward: float
    class Config: from_attributes = True

class LeaveRequestCreate(BaseModel):
    staff_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None
    handover_notes: Optional[str] = None

class LeaveRequestOut(BaseModel):
    id: int; staff_id: int; leave_type: str
    start_date: date; end_date: date; days_requested: float
    status: str; reason: Optional[str]
    class Config: from_attributes = True

class ApprovalAction(BaseModel):
    action: str  # "approve" | "reject"
    rejection_reason: Optional[str] = None


# ── Leave Policies ────────────────────────────────────────────────────────────

@router.get("/policies", response_model=List[PolicyOut])
def list_policies(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(LeavePolicy).all()

@router.post("/policies", response_model=PolicyOut, status_code=201)
def create_policy(data: PolicyCreate, db: Session = Depends(get_db),
                  _=Depends(require_admin)):
    if db.query(LeavePolicy).filter_by(leave_type=data.leave_type).first():
        raise HTTPException(409, "Policy for this leave type already exists")
    obj = LeavePolicy(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/policies/{id}", response_model=PolicyOut)
def update_policy(id: int, data: PolicyCreate, db: Session = Depends(get_db),
                  _=Depends(require_admin)):
    obj = db.query(LeavePolicy).get(id)
    if not obj: raise HTTPException(404, "Policy not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj


# ── Leave Balances ────────────────────────────────────────────────────────────

@router.get("/balances/{staff_id}", response_model=List[BalanceOut])
def get_balances(staff_id: int, academic_year_id: Optional[int] = None,
                 db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(LeaveBalance).filter_by(staff_id=staff_id)
    if academic_year_id:
        q = q.filter_by(academic_year_id=academic_year_id)
    return q.all()

@router.post("/balances/initialize")
def initialize_balances(staff_id: int, academic_year_id: int,
                        db: Session = Depends(get_db), _=Depends(require_admin)):
    """Create leave balances for a staff member based on active policies."""
    policies = db.query(LeavePolicy).all()
    created = 0
    for policy in policies:
        exists = db.query(LeaveBalance).filter_by(
            staff_id=staff_id, leave_type=policy.leave_type,
            academic_year_id=academic_year_id).first()
        if not exists:
            db.add(LeaveBalance(
                staff_id=staff_id,
                leave_type=policy.leave_type,
                academic_year_id=academic_year_id,
                entitled_days=policy.days_per_year,
            ))
            created += 1
    db.commit()
    return {"staff_id": staff_id, "balances_created": created}

@router.post("/balances/initialize-all")
def initialize_all_balances(academic_year_id: int,
                             db: Session = Depends(get_db), _=Depends(require_admin)):
    """Initialize leave balances for ALL active staff."""
    staff_list = db.query(StaffProfile).filter_by(employment_status="active").all()
    policies = db.query(LeavePolicy).all()
    total = 0
    for staff in staff_list:
        for policy in policies:
            exists = db.query(LeaveBalance).filter_by(
                staff_id=staff.id, leave_type=policy.leave_type,
                academic_year_id=academic_year_id).first()
            if not exists:
                db.add(LeaveBalance(
                    staff_id=staff.id,
                    leave_type=policy.leave_type,
                    academic_year_id=academic_year_id,
                    entitled_days=policy.days_per_year,
                ))
                total += 1
    db.commit()
    return {"staff_count": len(staff_list), "balances_created": total}


# ── Leave Requests ────────────────────────────────────────────────────────────

def _business_days(start: date, end: date) -> float:
    """Count weekdays between two dates inclusive."""
    from datetime import timedelta
    days = 0
    current = start
    while current <= end:
        if current.weekday() < 5:  # Mon–Fri
            days += 1
        current += timedelta(days=1)
    return float(days)

@router.get("/requests", response_model=List[LeaveRequestOut])
def list_requests(skip: int = 0, limit: int = 100,
                  staff_id: Optional[int] = None,
                  status: Optional[str] = None,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(LeaveRequest)
    if staff_id: q = q.filter_by(staff_id=staff_id)
    if status: q = q.filter(LeaveRequest.status == status)
    return q.order_by(LeaveRequest.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/requests", response_model=LeaveRequestOut, status_code=201)
def create_request(data: LeaveRequestCreate, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
    staff = db.query(StaffProfile).get(data.staff_id)
    if not staff: raise HTTPException(404, "Staff profile not found")
    days = _business_days(data.start_date, data.end_date)
    if days <= 0:
        raise HTTPException(400, "End date must be after start date")
    # Check balance
    balance = db.query(LeaveBalance).filter_by(
        staff_id=data.staff_id, leave_type=data.leave_type).first()
    if balance:
        remaining = balance.entitled_days + balance.carried_forward - balance.used_days
        if days > remaining:
            raise HTTPException(400, f"Insufficient leave balance. Available: {remaining} days")
    obj = LeaveRequest(
        staff_id=data.staff_id,
        leave_type=LeaveType(data.leave_type),
        start_date=data.start_date,
        end_date=data.end_date,
        days_requested=days,
        reason=data.reason,
        handover_notes=data.handover_notes,
    )
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/requests/{id}", response_model=LeaveRequestOut)
def get_request(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(LeaveRequest).get(id)
    if not obj: raise HTTPException(404, "Leave request not found")
    return obj

@router.put("/requests/{id}/action")
def action_request(id: int, data: ApprovalAction,
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    req = db.query(LeaveRequest).get(id)
    if not req: raise HTTPException(404, "Leave request not found")
    if req.status != LeaveStatus.PENDING:
        raise HTTPException(400, f"Request is already {req.status}")

    approver = db.query(StaffProfile).filter_by(user_id=current_user.id).first()

    if data.action == "approve":
        req.status = LeaveStatus.APPROVED
        req.approved_by_id = approver.id if approver else None
        req.approved_at = datetime.utcnow()
        # Deduct from balance
        balance = db.query(LeaveBalance).filter_by(
            staff_id=req.staff_id, leave_type=req.leave_type).first()
        if balance:
            balance.used_days += req.days_requested
    elif data.action == "reject":
        req.status = LeaveStatus.REJECTED
        req.rejection_reason = data.rejection_reason
    else:
        raise HTTPException(400, "action must be 'approve' or 'reject'")

    db.commit(); db.refresh(req)
    return {"id": req.id, "status": req.status}

@router.put("/requests/{id}/cancel")
def cancel_request(id: int, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    req = db.query(LeaveRequest).get(id)
    if not req: raise HTTPException(404, "Leave request not found")
    if req.status not in [LeaveStatus.PENDING, LeaveStatus.APPROVED]:
        raise HTTPException(400, "Cannot cancel this request")
    if req.status == LeaveStatus.APPROVED:
        # Restore balance
        balance = db.query(LeaveBalance).filter_by(
            staff_id=req.staff_id, leave_type=req.leave_type).first()
        if balance:
            balance.used_days = max(0, balance.used_days - req.days_requested)
    req.status = LeaveStatus.CANCELLED
    db.commit()
    return {"id": req.id, "status": req.status}
