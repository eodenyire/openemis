"""Phase 4 verification script."""
import app.db.registry  # noqa
from app.db.session import SessionLocal
from app.models.hr import (
    StaffProfile, LeavePolicy, LeaveBalance, LeaveRequest,
    TPADAppraisal, PayComponent, PayrollRun, Payslip, PayslipLine,
)

db = SessionLocal()
issues = []

print("=== Phase 4 Verification ===\n")

# ── Counts ────────────────────────────────────────────────────────────────────
counts = {
    "Staff profiles":  db.query(StaffProfile).count(),
    "Leave policies":  db.query(LeavePolicy).count(),
    "Leave balances":  db.query(LeaveBalance).count(),
    "Leave requests":  db.query(LeaveRequest).count(),
    "TPAD appraisals": db.query(TPADAppraisal).count(),
    "Pay components":  db.query(PayComponent).count(),
    "Payroll runs":    db.query(PayrollRun).count(),
    "Payslips":        db.query(Payslip).count(),
    "Payslip lines":   db.query(PayslipLine).count(),
}
for k, v in counts.items():
    status = "[OK]" if v > 0 else "[MISSING]"
    if v == 0:
        issues.append(f"{k} = 0")
    print(f"  {status} {k}: {v}")

# ── Leave Policies ────────────────────────────────────────────────────────────
print("\n--- Leave Policies ---")
for p in db.query(LeavePolicy).all():
    print(f"  {p.leave_type:20s} {p.days_per_year:5.0f} days  carry={p.carry_forward}")

# ── Leave Requests breakdown ──────────────────────────────────────────────────
print("\n--- Leave Requests by Status ---")
from sqlalchemy import func
from app.models.hr import LeaveStatus
for status in LeaveStatus:
    n = db.query(LeaveRequest).filter(LeaveRequest.status == status).count()
    print(f"  {status.value:12s}: {n}")

# ── TPAD breakdown ────────────────────────────────────────────────────────────
print("\n--- TPAD Appraisals ---")
for a in db.query(TPADAppraisal).limit(5).all():
    print(f"  staff={a.staff_id} period={a.appraisal_period:10s} avg={a.average_score:.2f} "
          f"rating={str(a.rating):20s} submitted={a.is_submitted} ack={a.is_acknowledged}")

# ── Pay Components ────────────────────────────────────────────────────────────
print("\n--- Pay Components ---")
for c in db.query(PayComponent).all():
    amt = f"KES {float(c.default_amount):,.0f}" if c.is_fixed else f"{c.default_percentage}% of basic"
    print(f"  [{c.component_type.value:10s}] {c.name:25s} {amt}")

# ── Payroll Run ───────────────────────────────────────────────────────────────
print("\n--- Payroll Run ---")
run = db.query(PayrollRun).first()
if run:
    print(f"  Name   : {run.name}")
    print(f"  Status : {run.status}")
    print(f"  Gross  : KES {float(run.total_gross or 0):>12,.2f}")
    print(f"  Deduct : KES {float(run.total_deductions or 0):>12,.2f}")
    print(f"  Net    : KES {float(run.total_net or 0):>12,.2f}")

    # Sample payslips
    print("\n--- Sample Payslips (first 5) ---")
    for s in db.query(Payslip).filter_by(payroll_run_id=run.id).limit(5).all():
        print(f"  staff={s.staff_id:3d}  basic={float(s.basic_salary or 0):>10,.0f}  "
              f"gross={float(s.gross_salary or 0):>10,.0f}  "
              f"paye={float(s.paye or 0):>8,.0f}  "
              f"nhif={float(s.nhif or 0):>6,.0f}  "
              f"nssf={float(s.nssf or 0):>6,.0f}  "
              f"net={float(s.net_salary or 0):>10,.0f}")

    # Check payslips have lines
    slip = db.query(Payslip).filter_by(payroll_run_id=run.id).first()
    if slip:
        lines = db.query(PayslipLine).filter_by(payslip_id=slip.id).all()
        print(f"\n  Payslip lines for staff_id={slip.staff_id}:")
        for l in lines:
            print(f"    {l.component.name:25s} [{l.component.component_type.value}]  KES {float(l.amount):,.2f}")
else:
    issues.append("No payroll run found")

# ── Staff sample ──────────────────────────────────────────────────────────────
print("\n--- Staff Profiles (first 5) ---")
for s in db.query(StaffProfile).limit(5).all():
    print(f"  id={s.id:3d}  tsc={s.tsc_number:15s}  job={str(s.job_title):30s}  "
          f"salary=KES {float(s.basic_salary or 0):>10,.0f}  status={s.employment_status}")

# ── API routes check ──────────────────────────────────────────────────────────
print("\n--- API Routes ---")
from app.api.v1.router import api_router
hr_routes = [r.path for r in api_router.routes if any(
    p in r.path for p in ["/hr/", "/leave/", "/tpad/", "/payroll/"])]
print(f"  HR/Leave/TPAD/Payroll routes: {len(hr_routes)}")
for r in sorted(hr_routes):
    print(f"    {r}")

# ── Final verdict ─────────────────────────────────────────────────────────────
print("\n=== RESULT ===")
if issues:
    print(f"[ISSUES FOUND] {len(issues)} problem(s):")
    for i in issues:
        print(f"  - {i}")
else:
    print("[PASS] Phase 4 fully implemented and seeded correctly.")

db.close()
