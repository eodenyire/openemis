"""Payroll endpoints — Pay components, payroll runs, payslips, Kenya statutory deductions."""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.hr import (
    PayComponent, PayComponentType, PayrollRun, PayrollStatus,
    Payslip, PayslipLine, StaffProfile,
)

router = APIRouter()


# ── Kenya PAYE Tax Bands 2024/2025 ────────────────────────────────────────────
# Monthly taxable income bands (KES)
PAYE_BANDS = [
    (24_000,   0.10),
    (8_333,    0.25),
    (467_667,  0.30),
    (300_000,  0.325),
    (float('inf'), 0.35),
]
PERSONAL_RELIEF = 2_400  # KES per month


def compute_paye(taxable_income: float) -> float:
    """Compute PAYE using Kenya 2024 tax bands."""
    tax = 0.0
    remaining = taxable_income
    for band, rate in PAYE_BANDS:
        if remaining <= 0:
            break
        taxable = min(remaining, band)
        tax += taxable * rate
        remaining -= taxable
    tax = max(0, tax - PERSONAL_RELIEF)
    return round(tax, 2)


def compute_nhif(gross: float) -> float:
    """NHIF contribution table (2024)."""
    bands = [
        (5_999, 150), (7_999, 300), (11_999, 400), (14_999, 500),
        (19_999, 600), (24_999, 750), (29_999, 850), (34_999, 900),
        (39_999, 950), (44_999, 1_000), (49_999, 1_100), (59_999, 1_200),
        (69_999, 1_300), (79_999, 1_400), (89_999, 1_500), (99_999, 1_600),
        (float('inf'), 1_700),
    ]
    for limit, amount in bands:
        if gross <= limit:
            return float(amount)
    return 1_700.0


def compute_nssf(gross: float) -> float:
    """NSSF Tier I + Tier II (NSSF Act 2013)."""
    tier1_limit = 7_000
    tier2_limit = 36_000
    tier1 = min(gross, tier1_limit) * 0.06
    tier2 = max(0, min(gross, tier2_limit) - tier1_limit) * 0.06
    return round(tier1 + tier2, 2)


def compute_housing_levy(gross: float) -> float:
    """Affordable Housing Levy — 1.5% of gross."""
    return round(gross * 0.015, 2)


# ── Schemas ───────────────────────────────────────────────────────────────────

class ComponentCreate(BaseModel):
    name: str; code: str
    component_type: str
    is_taxable: bool = True
    is_fixed: bool = True
    default_amount: float = 0
    default_percentage: float = 0
    description: Optional[str] = None

class ComponentOut(BaseModel):
    id: int; name: str; code: str; component_type: str
    is_taxable: bool; is_fixed: bool
    default_amount: Optional[Decimal]; default_percentage: float
    class Config: from_attributes = True

class PayrollRunCreate(BaseModel):
    name: str; month: int; year: int
    notes: Optional[str] = None

class PayrollRunOut(BaseModel):
    id: int; name: str; month: int; year: int; status: str
    total_gross: Optional[Decimal]; total_deductions: Optional[Decimal]
    total_net: Optional[Decimal]
    class Config: from_attributes = True

class PayslipOut(BaseModel):
    id: int; payroll_run_id: int; staff_id: int
    basic_salary: Optional[Decimal]; gross_salary: Optional[Decimal]
    total_deductions: Optional[Decimal]; net_salary: Optional[Decimal]
    paye: Optional[Decimal]; nhif: Optional[Decimal]
    nssf: Optional[Decimal]; housing_levy: Optional[Decimal]
    is_paid: bool
    class Config: from_attributes = True


# ── Pay Components ────────────────────────────────────────────────────────────

@router.get("/components", response_model=List[ComponentOut])
def list_components(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(PayComponent).filter_by(active=True).all()

@router.post("/components", response_model=ComponentOut, status_code=201)
def create_component(data: ComponentCreate, db: Session = Depends(get_db),
                     _=Depends(require_admin)):
    if db.query(PayComponent).filter_by(code=data.code).first():
        raise HTTPException(409, f"Component with code '{data.code}' already exists")
    obj = PayComponent(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/components/{id}", response_model=ComponentOut)
def update_component(id: int, data: ComponentCreate, db: Session = Depends(get_db),
                     _=Depends(require_admin)):
    obj = db.query(PayComponent).get(id)
    if not obj: raise HTTPException(404, "Component not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj


# ── Payroll Runs ──────────────────────────────────────────────────────────────

@router.get("/runs", response_model=List[PayrollRunOut])
def list_runs(skip: int = 0, limit: int = 24, db: Session = Depends(get_db),
              _=Depends(get_current_user)):
    return db.query(PayrollRun).order_by(
        PayrollRun.year.desc(), PayrollRun.month.desc()).offset(skip).limit(limit).all()

@router.post("/runs", response_model=PayrollRunOut, status_code=201)
def create_run(data: PayrollRunCreate, db: Session = Depends(get_db),
               _=Depends(require_admin)):
    if not (1 <= data.month <= 12):
        raise HTTPException(400, "Month must be 1–12")
    existing = db.query(PayrollRun).filter_by(month=data.month, year=data.year).first()
    if existing:
        raise HTTPException(409, f"Payroll run for {data.month}/{data.year} already exists")
    obj = PayrollRun(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/runs/{id}", response_model=PayrollRunOut)
def get_run(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(PayrollRun).get(id)
    if not obj: raise HTTPException(404, "Payroll run not found")
    return obj

@router.post("/runs/{id}/generate")
def generate_payslips(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    """
    Auto-generate payslips for all active staff.
    Computes PAYE, NHIF, NSSF, Housing Levy automatically.
    """
    run = db.query(PayrollRun).get(id)
    if not run: raise HTTPException(404, "Payroll run not found")
    if run.status != PayrollStatus.DRAFT:
        raise HTTPException(400, "Can only generate payslips for DRAFT runs")

    staff_list = db.query(StaffProfile).filter_by(employment_status="active").all()
    components = db.query(PayComponent).filter_by(active=True).all()
    earnings = [c for c in components if c.component_type == PayComponentType.EARNING]
    deductions = [c for c in components if c.component_type == PayComponentType.DEDUCTION]

    created = 0
    total_gross = Decimal("0")
    total_deductions = Decimal("0")
    total_net = Decimal("0")

    for staff in staff_list:
        # Skip if payslip already exists
        if db.query(Payslip).filter_by(payroll_run_id=id, staff_id=staff.id).first():
            continue

        basic = float(staff.basic_salary or 0)
        gross = basic

        payslip = Payslip(
            payroll_run_id=id,
            staff_id=staff.id,
            basic_salary=Decimal(str(basic)),
        )
        db.add(payslip); db.flush()

        # Add earning components
        for comp in earnings:
            amount = float(comp.default_amount or 0)
            if not comp.is_fixed:
                amount = basic * (float(comp.default_percentage or 0) / 100)
            if amount > 0:
                db.add(PayslipLine(
                    payslip_id=payslip.id,
                    component_id=comp.id,
                    amount=Decimal(str(round(amount, 2))),
                    description=comp.name,
                ))
                gross += amount

        # Statutory deductions
        paye = compute_paye(gross)
        nhif = compute_nhif(gross)
        nssf = compute_nssf(gross)
        housing = compute_housing_levy(gross)
        statutory_total = paye + nhif + nssf + housing

        # Custom deductions
        custom_deductions = 0.0
        for comp in deductions:
            amount = float(comp.default_amount or 0)
            if not comp.is_fixed:
                amount = gross * (float(comp.default_percentage or 0) / 100)
            if amount > 0:
                db.add(PayslipLine(
                    payslip_id=payslip.id,
                    component_id=comp.id,
                    amount=Decimal(str(round(amount, 2))),
                    description=comp.name,
                ))
                custom_deductions += amount

        total_ded = statutory_total + custom_deductions
        net = gross - total_ded

        payslip.gross_salary = Decimal(str(round(gross, 2)))
        payslip.paye = Decimal(str(paye))
        payslip.nhif = Decimal(str(nhif))
        payslip.nssf = Decimal(str(nssf))
        payslip.housing_levy = Decimal(str(housing))
        payslip.total_deductions = Decimal(str(round(total_ded, 2)))
        payslip.net_salary = Decimal(str(round(net, 2)))

        total_gross += payslip.gross_salary
        total_deductions += payslip.total_deductions
        total_net += payslip.net_salary
        created += 1

    run.total_gross = total_gross
    run.total_deductions = total_deductions
    run.total_net = total_net
    db.commit()
    return {"payroll_run_id": id, "payslips_generated": created,
            "total_gross": float(total_gross), "total_net": float(total_net)}

@router.put("/runs/{id}/approve")
def approve_run(id: int, db: Session = Depends(get_db),
                current_user=Depends(require_admin)):
    run = db.query(PayrollRun).get(id)
    if not run: raise HTTPException(404, "Payroll run not found")
    if run.status != PayrollStatus.DRAFT:
        raise HTTPException(400, "Only DRAFT runs can be approved")
    run.status = PayrollStatus.APPROVED
    run.approved_by_id = current_user.id
    run.approved_at = datetime.utcnow()
    db.commit()
    return {"id": run.id, "status": run.status}

@router.put("/runs/{id}/mark-paid")
def mark_paid(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    run = db.query(PayrollRun).get(id)
    if not run: raise HTTPException(404, "Payroll run not found")
    if run.status != PayrollStatus.APPROVED:
        raise HTTPException(400, "Only APPROVED runs can be marked as paid")
    payslips = db.query(Payslip).filter_by(payroll_run_id=id).all()
    for p in payslips:
        p.is_paid = True
        p.paid_at = datetime.utcnow()
    run.status = PayrollStatus.PAID
    db.commit()
    return {"id": run.id, "status": run.status, "payslips_paid": len(payslips)}


# ── Payslips ──────────────────────────────────────────────────────────────────

@router.get("/runs/{id}/payslips", response_model=List[PayslipOut])
def list_payslips(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Payslip).filter_by(payroll_run_id=id).all()

@router.get("/payslips/{id}", response_model=PayslipOut)
def get_payslip(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Payslip).get(id)
    if not obj: raise HTTPException(404, "Payslip not found")
    return obj

@router.get("/payslips/{id}/lines")
def get_payslip_lines(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    payslip = db.query(Payslip).get(id)
    if not payslip: raise HTTPException(404, "Payslip not found")
    lines = db.query(PayslipLine).filter_by(payslip_id=id).all()
    return [{"id": l.id, "component": l.component.name,
             "type": l.component.component_type, "amount": float(l.amount)} for l in lines]

@router.get("/staff/{staff_id}/payslips", response_model=List[PayslipOut])
def staff_payslips(staff_id: int, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
    return db.query(Payslip).filter_by(staff_id=staff_id).order_by(
        Payslip.created_at.desc()).all()
