"""
HR models — Staff records, Leave management, TPAD appraisal, Payroll.
Kenya-specific: TPAD (Teacher Performance Appraisal & Development),
NHIF, NSSF, PAYE tax bands, TSC number.
"""
import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    ForeignKey, Text, Enum, Float, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


# ── Enums ─────────────────────────────────────────────────────────────────────

class EmploymentType(str, enum.Enum):
    PERMANENT = "permanent"
    CONTRACT = "contract"
    INTERN = "intern"
    VOLUNTEER = "volunteer"
    PART_TIME = "part_time"


class EmploymentStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    RETIRED = "retired"


class LeaveType(str, enum.Enum):
    ANNUAL = "annual"
    SICK = "sick"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    COMPASSIONATE = "compassionate"
    STUDY = "study"
    UNPAID = "unpaid"
    OTHER = "other"


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class TPADRating(str, enum.Enum):
    OUTSTANDING = "outstanding"       # 4.5 – 5.0
    EXCEEDS = "exceeds"               # 3.5 – 4.4
    MEETS = "meets"                   # 2.5 – 3.4
    BELOW = "below"                   # 1.5 – 2.4
    UNSATISFACTORY = "unsatisfactory" # 0.0 – 1.4


class PayrollStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


class PayComponentType(str, enum.Enum):
    EARNING = "earning"
    DEDUCTION = "deduction"


# ── Staff Profile (extends Teacher for non-teaching staff too) ────────────────

class StaffProfile(Base):
    """
    Extended HR profile for all staff (teachers + admin + support).
    Links to Teacher or User depending on role.
    """
    __tablename__ = "staff_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), unique=True, nullable=True)

    # Kenya-specific identifiers
    tsc_number = Column(String(50), unique=True, nullable=True, index=True)
    national_id = Column(String(20), unique=True, nullable=True)
    kra_pin = Column(String(20), unique=True, nullable=True)
    nhif_number = Column(String(20), nullable=True)
    nssf_number = Column(String(20), nullable=True)

    # Employment details
    employment_type = Column(Enum(EmploymentType), default=EmploymentType.PERMANENT)
    employment_status = Column(Enum(EmploymentStatus), default=EmploymentStatus.ACTIVE)
    job_title = Column(String(200))
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    reporting_to_id = Column(Integer, ForeignKey("staff_profiles.id"), nullable=True)
    hire_date = Column(Date, nullable=False)
    confirmation_date = Column(Date, nullable=True)
    termination_date = Column(Date, nullable=True)
    termination_reason = Column(Text, nullable=True)

    # Salary
    basic_salary = Column(Numeric(12, 2), default=0)
    bank_name = Column(String(100))
    bank_account = Column(String(50))
    bank_branch = Column(String(100))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="staff_profile")
    teacher = relationship("Teacher", backref="staff_profile", foreign_keys=[teacher_id])
    department = relationship("Department")
    reporting_to = relationship("StaffProfile", remote_side=[id], backref="direct_reports")
    leave_balances = relationship("LeaveBalance", back_populates="staff")
    leave_requests = relationship("LeaveRequest", back_populates="staff",
                                  foreign_keys="LeaveRequest.staff_id")
    tpad_appraisals = relationship("TPADAppraisal", back_populates="staff",
                                   foreign_keys="TPADAppraisal.staff_id")
    payslips = relationship("Payslip", back_populates="staff")


# ── Leave Management ──────────────────────────────────────────────────────────

class LeavePolicy(Base):
    """Annual leave entitlement per leave type."""
    __tablename__ = "leave_policies"

    id = Column(Integer, primary_key=True, index=True)
    leave_type = Column(Enum(LeaveType), nullable=False, unique=True)
    days_per_year = Column(Float, nullable=False)
    carry_forward = Column(Boolean, default=False)
    max_carry_forward_days = Column(Float, default=0)
    requires_approval = Column(Boolean, default=True)
    description = Column(Text)


class LeaveBalance(Base):
    """Current leave balance per staff per leave type per year."""
    __tablename__ = "leave_balances"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff_profiles.id"), nullable=False)
    leave_type = Column(Enum(LeaveType), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    entitled_days = Column(Float, default=0)
    used_days = Column(Float, default=0)
    carried_forward = Column(Float, default=0)

    staff = relationship("StaffProfile", back_populates="leave_balances")
    academic_year = relationship("AcademicYear")

    @property
    def remaining_days(self):
        return self.entitled_days + self.carried_forward - self.used_days


class LeaveRequest(Base):
    """Staff leave application."""
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff_profiles.id"), nullable=False)
    leave_type = Column(Enum(LeaveType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_requested = Column(Float, nullable=False)
    reason = Column(Text)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING)
    approved_by_id = Column(Integer, ForeignKey("staff_profiles.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    handover_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    staff = relationship("StaffProfile", back_populates="leave_requests",
                         foreign_keys=[staff_id])
    approved_by = relationship("StaffProfile", foreign_keys=[approved_by_id])


# ── TPAD Appraisal (Kenya TSC standard) ──────────────────────────────────────

class TPADAppraisal(Base):
    """
    Teacher Performance Appraisal & Development (TPAD) — Kenya TSC requirement.
    Two appraisals per year: mid-year and end-of-year.
    """
    __tablename__ = "tpad_appraisals"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff_profiles.id"), nullable=False)
    appraiser_id = Column(Integer, ForeignKey("staff_profiles.id"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    appraisal_period = Column(String(20), nullable=False)  # "mid_year" | "end_year"

    # TPAD Competency Areas (scored 1–5)
    professional_knowledge = Column(Float, default=0)       # Knowledge of subject
    lesson_planning = Column(Float, default=0)              # Preparation & planning
    classroom_management = Column(Float, default=0)         # Classroom environment
    teaching_methodology = Column(Float, default=0)         # Delivery & pedagogy
    student_assessment = Column(Float, default=0)           # Assessment practices
    professional_development = Column(Float, default=0)     # CPD & self-improvement
    co_curricular = Column(Float, default=0)                # Extra-curricular involvement
    community_engagement = Column(Float, default=0)         # Parent/community relations

    # Computed
    total_score = Column(Float, default=0)
    average_score = Column(Float, default=0)
    rating = Column(Enum(TPADRating), nullable=True)

    # Narrative
    strengths = Column(Text)
    areas_for_improvement = Column(Text)
    targets_next_period = Column(Text)
    staff_comments = Column(Text)
    appraiser_comments = Column(Text)

    # Workflow
    is_submitted = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    staff = relationship("StaffProfile", back_populates="tpad_appraisals",
                         foreign_keys=[staff_id])
    appraiser = relationship("StaffProfile", foreign_keys=[appraiser_id])
    academic_year = relationship("AcademicYear")


# ── Payroll ───────────────────────────────────────────────────────────────────

class PayComponent(Base):
    """Reusable pay component — allowances, deductions, taxes."""
    __tablename__ = "pay_components"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), nullable=False, unique=True)
    component_type = Column(Enum(PayComponentType), nullable=False)
    is_taxable = Column(Boolean, default=True)
    is_fixed = Column(Boolean, default=True)       # fixed amount vs % of basic
    default_amount = Column(Numeric(12, 2), default=0)
    default_percentage = Column(Float, default=0)  # % of basic salary
    description = Column(Text)
    active = Column(Boolean, default=True)


class PayrollRun(Base):
    """Monthly payroll run for all staff."""
    __tablename__ = "payroll_runs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)       # e.g. "January 2026 Payroll"
    month = Column(Integer, nullable=False)           # 1–12
    year = Column(Integer, nullable=False)
    status = Column(Enum(PayrollStatus), default=PayrollStatus.DRAFT)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    total_gross = Column(Numeric(14, 2), default=0)
    total_deductions = Column(Numeric(14, 2), default=0)
    total_net = Column(Numeric(14, 2), default=0)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    approved_by = relationship("User")
    payslips = relationship("Payslip", back_populates="payroll_run")


class Payslip(Base):
    """Individual staff payslip for a payroll run."""
    __tablename__ = "payslips"

    id = Column(Integer, primary_key=True, index=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff_profiles.id"), nullable=False)

    basic_salary = Column(Numeric(12, 2), default=0)
    gross_salary = Column(Numeric(12, 2), default=0)
    total_deductions = Column(Numeric(12, 2), default=0)
    net_salary = Column(Numeric(12, 2), default=0)

    # Kenya statutory deductions
    paye = Column(Numeric(10, 2), default=0)        # Pay As You Earn tax
    nhif = Column(Numeric(10, 2), default=0)        # National Hospital Insurance Fund
    nssf = Column(Numeric(10, 2), default=0)        # National Social Security Fund
    housing_levy = Column(Numeric(10, 2), default=0)  # Affordable Housing Levy (1.5%)

    is_paid = Column(Boolean, default=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    payment_reference = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    payroll_run = relationship("PayrollRun", back_populates="payslips")
    staff = relationship("StaffProfile", back_populates="payslips")
    lines = relationship("PayslipLine", back_populates="payslip")


class PayslipLine(Base):
    """Individual earning/deduction line on a payslip."""
    __tablename__ = "payslip_lines"

    id = Column(Integer, primary_key=True, index=True)
    payslip_id = Column(Integer, ForeignKey("payslips.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("pay_components.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String(200))

    payslip = relationship("Payslip", back_populates="lines")
    component = relationship("PayComponent")
