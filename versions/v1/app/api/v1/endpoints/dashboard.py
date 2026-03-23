"""Role-based dashboard summary endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.models.people import Teacher, Student
from app.models.attendance import AttendanceLine, AttendanceSheet
from app.models.fees import StudentFeeInvoice, FeePayment
from app.models.exam import Exam
from app.models.assignment import Assignment
from app.models.admission import Admission
from datetime import date

router = APIRouter()


@router.get("/summary")
def dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    role = current_user.role

    if role in (UserRole.SUPER_ADMIN, UserRole.ADMIN):
        return _super_admin_summary(db)
    elif role == UserRole.SCHOOL_ADMIN:
        return _school_admin_summary(db)
    elif role in (UserRole.TEACHER, UserRole.ACADEMIC_DIRECTOR):
        return _teacher_summary(db, current_user)
    elif role == UserRole.STUDENT:
        return _student_summary(db, current_user)
    elif role == UserRole.PARENT:
        return _parent_summary(db, current_user)
    elif role == UserRole.FINANCE_OFFICER:
        return _finance_summary(db)
    elif role == UserRole.REGISTRAR:
        return _registrar_summary(db)
    else:
        return _generic_summary(db, current_user)


def _super_admin_summary(db):
    return {
        "role": "super_admin",
        "total_students": db.query(func.count(Student.id)).scalar(),
        "total_teachers": db.query(func.count(Teacher.id)).scalar(),
        "total_users": db.query(func.count(User.id)).scalar(),
        "active_users": db.query(func.count(User.id)).filter(User.is_active == True).scalar(),
        "system_status": "healthy",
    }


def _school_admin_summary(db):
    today = date.today()
    total_students = db.query(func.count(Student.id)).scalar()
    total_teachers = db.query(func.count(Teacher.id)).scalar()

    # Attendance today
    today_sheets = db.query(AttendanceSheet).filter(
        func.date(AttendanceSheet.attendance_date) == today
    ).all()
    sheet_ids = [s.id for s in today_sheets]
    present_today = 0
    if sheet_ids:
        from app.models.attendance import AttendanceStatus
        present_today = db.query(func.count(AttendanceLine.id)).filter(
            AttendanceLine.sheet_id.in_(sheet_ids),
            AttendanceLine.status == AttendanceStatus.PRESENT,
        ).scalar()

    # Fee collection
    total_collected = db.query(func.coalesce(func.sum(FeePayment.amount), 0)).scalar()
    total_outstanding = db.query(
        func.coalesce(func.sum(StudentFeeInvoice.total_amount - StudentFeeInvoice.paid_amount), 0)
    ).scalar()

    return {
        "role": "school_admin",
        "total_students": total_students,
        "total_teachers": total_teachers,
        "attendance_today": present_today,
        "fee_collected_kes": float(total_collected),
        "fee_outstanding_kes": float(total_outstanding),
        "upcoming_exams": db.query(func.count(Exam.id)).filter(Exam.start_time >= func.now()).scalar(),
    }


def _teacher_summary(db, user):
    teacher = db.query(Teacher).filter(Teacher.user_id == user.id).first()
    teacher_id = teacher.id if teacher else None

    pending_assignments = 0
    if teacher_id:
        pending_assignments = db.query(func.count(Assignment.id)).filter(
            Assignment.faculty_id == teacher_id,
            Assignment.state == "published",
        ).scalar()

    return {
        "role": "teacher",
        "teacher_id": teacher_id,
        "assignments_published": pending_assignments,
        "upcoming_exams": db.query(func.count(Exam.id)).filter(Exam.start_time >= func.now()).scalar(),
        "message": f"Welcome, {user.first_name or user.username}",
    }


def _student_summary(db, user):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        return {"role": "student", "message": "No student profile linked"}

    invoices = db.query(StudentFeeInvoice).filter(
        StudentFeeInvoice.student_id == student.id,
        StudentFeeInvoice.paid_amount < StudentFeeInvoice.total_amount,
    ).all()
    fees_due = sum(i.total_amount - i.paid_amount for i in invoices)

    return {
        "role": "student",
        "student_id": student.id,
        "admission_number": student.admission_number,
        "fees_due_kes": float(fees_due),
        "pending_assignments": db.query(func.count(Assignment.id)).scalar(),
        "message": f"Welcome, {student.first_name}",
    }


def _parent_summary(db, user):
    from app.models.people import Parent
    parent = db.query(Parent).filter(Parent.user_id == user.id).first()
    if not parent:
        return {"role": "parent", "message": "No parent profile linked"}

    children = parent.students
    child_ids = [c.id for c in children]
    fees_due = 0
    if child_ids:
        invoices = db.query(StudentFeeInvoice).filter(
            StudentFeeInvoice.student_id.in_(child_ids),
            StudentFeeInvoice.paid_amount < StudentFeeInvoice.total_amount,
        ).all()
        fees_due = sum(i.total_amount - i.paid_amount for i in invoices)

    return {
        "role": "parent",
        "children_count": len(children),
        "fees_due_kes": float(fees_due),
        "message": f"Welcome, {user.first_name or user.username}",
    }


def _finance_summary(db):
    total_collected = db.query(func.coalesce(func.sum(FeePayment.amount), 0)).scalar()
    total_invoiced = db.query(func.coalesce(func.sum(StudentFeeInvoice.total_amount), 0)).scalar()
    total_outstanding = float(total_invoiced) - float(total_collected)
    return {
        "role": "finance_officer",
        "total_invoiced_kes": float(total_invoiced),
        "total_collected_kes": float(total_collected),
        "total_outstanding_kes": total_outstanding,
        "total_payments": db.query(func.count(FeePayment.id)).scalar(),
    }


def _registrar_summary(db):
    return {
        "role": "registrar",
        "total_students": db.query(func.count(Student.id)).scalar(),
        "total_admissions": db.query(func.count(Admission.id)).scalar(),
    }


def _generic_summary(db, user):
    return {
        "role": user.role.value,
        "message": f"Welcome, {user.first_name or user.username}",
    }
