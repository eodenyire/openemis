"""Phase 4 seed — HR, Leave, TPAD Appraisal, Payroll."""
import sys, random
from datetime import date, datetime, timedelta
from decimal import Decimal

import app.db.registry  # noqa — must be first

from app.db.session import SessionLocal
from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.people import Teacher
from app.models.core import Department, AcademicYear
from app.models.hr import (
    StaffProfile, EmploymentType, EmploymentStatus,
    LeavePolicy, LeaveBalance, LeaveRequest, LeaveType, LeaveStatus,
    TPADAppraisal, TPADRating,
    PayComponent, PayComponentType, PayrollRun, PayrollStatus,
    Payslip, PayslipLine,
)

Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("=== Phase 4 Seed ===")

# ── Base data ─────────────────────────────────────────────────────────────────
year = db.query(AcademicYear).first()
teachers = db.query(Teacher).limit(20).all()
dept = db.query(Department).first()

if not year:
    print("[SKIP] No academic year found — run seed_kenya.py first")
    sys.exit(0)
if not teachers:
    print("[SKIP] No teachers found — run seed_kenya.py first")
    sys.exit(0)

print(f"[INFO] {len(teachers)} teachers, year={year.name}")

# ── Staff Profiles ────────────────────────────────────────────────────────────
JOB_TITLES = [
    "Class Teacher", "Subject Teacher", "Head of Department",
    "Deputy Principal", "Principal", "School Counselor",
    "Librarian", "Lab Technician", "Administrative Officer", "Bursar",
]
SALARY_RANGES = {
    "Class Teacher": (35_000, 55_000),
    "Subject Teacher": (38_000, 60_000),
    "Head of Department": (65_000, 85_000),
    "Deputy Principal": (90_000, 120_000),
    "Principal": (130_000, 180_000),
    "School Counselor": (40_000, 60_000),
    "Librarian": (35_000, 50_000),
    "Lab Technician": (30_000, 45_000),
    "Administrative Officer": (30_000, 50_000),
    "Bursar": (55_000, 80_000),
}

staff_profiles = []
created_count = 0
for i, teacher in enumerate(teachers):
    existing = db.query(StaffProfile).filter_by(user_id=teacher.user_id).first()
    if existing:
        staff_profiles.append(existing)
        continue
    job = JOB_TITLES[i % len(JOB_TITLES)]
    sal_min, sal_max = SALARY_RANGES[job]
    salary = round(random.uniform(sal_min, sal_max), -2)  # round to nearest 100
    tsc = f"TSC{100000 + i:06d}"
    profile = StaffProfile(
        user_id=teacher.user_id,
        teacher_id=teacher.id,
        tsc_number=tsc,
        national_id=f"3{random.randint(1000000, 9999999)}",
        kra_pin=f"A{random.randint(100000000, 999999999)}Z",
        nhif_number=f"NHIF{random.randint(100000, 999999)}",
        nssf_number=f"NSSF{random.randint(100000, 999999)}",
        employment_type=EmploymentType.PERMANENT,
        employment_status=EmploymentStatus.ACTIVE,
        job_title=job,
        department_id=dept.id if dept else None,
        hire_date=date(2020, 1, 15) + timedelta(days=i * 30),
        basic_salary=Decimal(str(salary)),
        bank_name=random.choice(["KCB Bank", "Equity Bank", "Co-operative Bank",
                                  "NCBA Bank", "Absa Bank"]),
        bank_account=f"{random.randint(10000000, 99999999)}",
    )
    db.add(profile); db.flush()
    staff_profiles.append(profile)
    created_count += 1

db.commit()
print(f"[OK] {created_count} staff profiles created ({len(staff_profiles)} total)")

# ── Leave Policies ────────────────────────────────────────────────────────────
POLICIES = [
    (LeaveType.ANNUAL,        21,  True,  10),
    (LeaveType.SICK,          14,  False,  0),
    (LeaveType.MATERNITY,     90,  False,  0),
    (LeaveType.PATERNITY,     14,  False,  0),
    (LeaveType.COMPASSIONATE,  5,  False,  0),
    (LeaveType.STUDY,         10,  False,  0),
    (LeaveType.UNPAID,         0,  False,  0),
]
policy_count = 0
for ltype, days, carry, max_carry in POLICIES:
    if not db.query(LeavePolicy).filter_by(leave_type=ltype).first():
        db.add(LeavePolicy(
            leave_type=ltype,
            days_per_year=days,
            carry_forward=carry,
            max_carry_forward_days=max_carry,
        ))
        policy_count += 1
db.commit()
print(f"[OK] {policy_count} leave policies created")

# ── Leave Balances ────────────────────────────────────────────────────────────
policies = db.query(LeavePolicy).all()
balance_count = 0
for staff in staff_profiles:
    for policy in policies:
        if not db.query(LeaveBalance).filter_by(
                staff_id=staff.id, leave_type=policy.leave_type,
                academic_year_id=year.id).first():
            db.add(LeaveBalance(
                staff_id=staff.id,
                leave_type=policy.leave_type,
                academic_year_id=year.id,
                entitled_days=policy.days_per_year,
                used_days=0,
                carried_forward=random.choice([0, 0, 0, 3, 5]) if policy.carry_forward else 0,
            ))
            balance_count += 1
db.commit()
print(f"[OK] {balance_count} leave balances initialized")

# ── Leave Requests ────────────────────────────────────────────────────────────
request_count = 0
approver = staff_profiles[0] if staff_profiles else None
for staff in staff_profiles[1:8]:  # 7 staff with leave requests
    ltype = random.choice([LeaveType.ANNUAL, LeaveType.SICK])
    start = date(2026, random.randint(1, 3), random.randint(1, 20))
    end = start + timedelta(days=random.randint(2, 5))
    days = sum(1 for i in range((end - start).days + 1)
               if (start + timedelta(i)).weekday() < 5)
    if not db.query(LeaveRequest).filter_by(staff_id=staff.id, leave_type=ltype).first():
        status = random.choice([LeaveStatus.APPROVED, LeaveStatus.APPROVED,
                                 LeaveStatus.PENDING, LeaveStatus.REJECTED])
        req = LeaveRequest(
            staff_id=staff.id,
            leave_type=ltype,
            start_date=start,
            end_date=end,
            days_requested=float(days),
            reason="Personal reasons" if ltype == LeaveType.ANNUAL else "Medical appointment",
            status=status,
            approved_by_id=approver.id if status == LeaveStatus.APPROVED and approver else None,
            approved_at=datetime.utcnow() if status == LeaveStatus.APPROVED else None,
        )
        db.add(req); db.flush()
        # Update balance if approved
        if status == LeaveStatus.APPROVED:
            bal = db.query(LeaveBalance).filter_by(
                staff_id=staff.id, leave_type=ltype, academic_year_id=year.id).first()
            if bal:
                bal.used_days += days
        request_count += 1
db.commit()
print(f"[OK] {request_count} leave requests created")

# ── TPAD Appraisals ───────────────────────────────────────────────────────────
def tpad_rating(avg):
    if avg >= 4.5: return TPADRating.OUTSTANDING
    if avg >= 3.5: return TPADRating.EXCEEDS
    if avg >= 2.5: return TPADRating.MEETS
    if avg >= 1.5: return TPADRating.BELOW
    return TPADRating.UNSATISFACTORY

COMPETENCY_FIELDS = [
    "professional_knowledge", "lesson_planning", "classroom_management",
    "teaching_methodology", "student_assessment", "professional_development",
    "co_curricular", "community_engagement",
]
appraiser = staff_profiles[0] if len(staff_profiles) > 1 else None
tpad_count = 0
for staff in staff_profiles[1:11]:  # 10 staff get appraisals
    for period in ["mid_year", "end_year"]:
        if db.query(TPADAppraisal).filter_by(
                staff_id=staff.id, academic_year_id=year.id,
                appraisal_period=period).first():
            continue
        scores = {f: round(random.uniform(2.5, 5.0), 1) for f in COMPETENCY_FIELDS}
        avg = round(sum(scores.values()) / len(scores), 2)
        appraisal = TPADAppraisal(
            staff_id=staff.id,
            appraiser_id=appraiser.id if appraiser else staff.id,
            academic_year_id=year.id,
            appraisal_period=period,
            **scores,
            total_score=round(sum(scores.values()), 2),
            average_score=avg,
            rating=tpad_rating(avg),
            strengths="Excellent classroom management and student engagement.",
            areas_for_improvement="Needs to incorporate more ICT tools in teaching.",
            targets_next_period="Complete one CPD course per term.",
            appraiser_comments="Good performance overall. Keep up the good work.",
            is_submitted=True,
            is_acknowledged=period == "mid_year",
            submitted_at=datetime.utcnow(),
            acknowledged_at=datetime.utcnow() if period == "mid_year" else None,
        )
        db.add(appraisal)
        tpad_count += 1
db.commit()
print(f"[OK] {tpad_count} TPAD appraisals created")

# ── Pay Components ────────────────────────────────────────────────────────────
COMPONENTS = [
    # Earnings
    ("House Allowance",       "HOUSE_ALLOW",  "earning",   True,  True,  5_000, 0),
    ("Transport Allowance",   "TRANS_ALLOW",  "earning",   True,  True,  3_000, 0),
    ("Medical Allowance",     "MED_ALLOW",    "earning",   False, True,  2_000, 0),
    ("Hardship Allowance",    "HARD_ALLOW",   "earning",   True,  False, 0,     10),  # 10% of basic
    # Deductions
    ("SACCO Loan",            "SACCO_LOAN",   "deduction", False, True,  2_000, 0),
    ("Staff Welfare",         "WELFARE",      "deduction", False, True,    500, 0),
]
comp_count = 0
for name, code, ctype, taxable, fixed, amount, pct in COMPONENTS:
    if not db.query(PayComponent).filter_by(code=code).first():
        db.add(PayComponent(
            name=name, code=code,
            component_type=PayComponentType(ctype),
            is_taxable=taxable, is_fixed=fixed,
            default_amount=Decimal(str(amount)),
            default_percentage=pct,
        ))
        comp_count += 1
db.commit()
print(f"[OK] {comp_count} pay components created")

# ── Payroll Run — January 2026 ────────────────────────────────────────────────
run = db.query(PayrollRun).filter_by(month=1, year=2026).first()
if not run:
    run = PayrollRun(name="January 2026 Payroll", month=1, year=2026)
    db.add(run); db.commit(); db.refresh(run)
    print(f"[OK] Payroll run created: {run.name} (id={run.id})")
else:
    print(f"[SKIP] Payroll run already exists: {run.name}")

# Generate payslips
components = db.query(PayComponent).filter_by(active=True).all()
earnings = [c for c in components if c.component_type == PayComponentType.EARNING]
deductions_list = [c for c in components if c.component_type == PayComponentType.DEDUCTION]

def compute_paye(taxable):
    bands = [(24_000, 0.10), (8_333, 0.25), (467_667, 0.30),
             (300_000, 0.325), (float('inf'), 0.35)]
    tax, remaining = 0.0, taxable
    for band, rate in bands:
        if remaining <= 0: break
        tax += min(remaining, band) * rate
        remaining -= band
    return max(0, round(tax - 2_400, 2))

def compute_nhif(gross):
    for limit, amt in [(5999,150),(7999,300),(11999,400),(14999,500),(19999,600),
                        (24999,750),(29999,850),(34999,900),(39999,950),(44999,1000),
                        (49999,1100),(59999,1200),(69999,1300),(79999,1400),
                        (89999,1500),(99999,1600)]:
        if gross <= limit: return float(amt)
    return 1700.0

def compute_nssf(gross):
    t1 = min(gross, 7000) * 0.06
    t2 = max(0, min(gross, 36000) - 7000) * 0.06
    return round(t1 + t2, 2)

payslip_count = 0
total_gross = Decimal("0")
total_ded = Decimal("0")
total_net = Decimal("0")

for staff in staff_profiles:
    if db.query(Payslip).filter_by(payroll_run_id=run.id, staff_id=staff.id).first():
        continue
    basic = float(staff.basic_salary or 0)
    gross = basic
    payslip = Payslip(payroll_run_id=run.id, staff_id=staff.id,
                      basic_salary=Decimal(str(basic)))
    db.add(payslip); db.flush()

    for comp in earnings:
        amt = float(comp.default_amount or 0)
        if not comp.is_fixed:
            amt = basic * (float(comp.default_percentage or 0) / 100)
        if amt > 0:
            db.add(PayslipLine(payslip_id=payslip.id, component_id=comp.id,
                               amount=Decimal(str(round(amt, 2))), description=comp.name))
            gross += amt

    paye = compute_paye(gross)
    nhif = compute_nhif(gross)
    nssf = compute_nssf(gross)
    housing = round(gross * 0.015, 2)
    custom = 0.0
    for comp in deductions_list:
        amt = float(comp.default_amount or 0)
        if not comp.is_fixed:
            amt = gross * (float(comp.default_percentage or 0) / 100)
        if amt > 0:
            db.add(PayslipLine(payslip_id=payslip.id, component_id=comp.id,
                               amount=Decimal(str(round(amt, 2))), description=comp.name))
            custom += amt

    total_d = paye + nhif + nssf + housing + custom
    net = gross - total_d

    payslip.gross_salary = Decimal(str(round(gross, 2)))
    payslip.paye = Decimal(str(paye))
    payslip.nhif = Decimal(str(nhif))
    payslip.nssf = Decimal(str(nssf))
    payslip.housing_levy = Decimal(str(housing))
    payslip.total_deductions = Decimal(str(round(total_d, 2)))
    payslip.net_salary = Decimal(str(round(net, 2)))

    total_gross += payslip.gross_salary
    total_ded += payslip.total_deductions
    total_net += payslip.net_salary
    payslip_count += 1

run.total_gross = total_gross
run.total_deductions = total_ded
run.total_net = total_net
db.commit()
print(f"[OK] {payslip_count} payslips generated")
print(f"     Gross: KES {float(total_gross):,.2f}")
print(f"     Deductions: KES {float(total_ded):,.2f}")
print(f"     Net: KES {float(total_net):,.2f}")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n=== Phase 4 Seed Complete ===")
print(f"  Staff profiles  : {len(staff_profiles)}")
print(f"  Leave policies  : {policy_count}")
print(f"  Leave balances  : {balance_count}")
print(f"  Leave requests  : {request_count}")
print(f"  TPAD appraisals : {tpad_count}")
print(f"  Pay components  : {comp_count}")
print(f"  Payslips        : {payslip_count}")
db.close()
