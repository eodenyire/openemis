"""
Reporting module — dedicated endpoint for every report across all modules.
All reports available in Excel (.xlsx) and PDF formats.

Sections:
  /reports/students/    — student list, performance, attendance, health
  /reports/staff/       — teacher directory, staff profiles, TPAD, leave, payroll
  /reports/finance/     — fee collection, outstanding, payment methods
  /reports/academic/    — exam results, CBC report cards, LMS, lesson plans
  /reports/library/     — catalogue, borrowing records, overdue
  /reports/hostel/      — occupancy, allocations
  /reports/transport/   — route manifest
  /reports/health/      — clinic visits, vaccinations
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user

# Report generators
from app.reports import students as rpt_students
from app.reports import staff as rpt_staff
from app.reports import finance as rpt_finance
from app.reports import academic as rpt_academic
from app.reports import support_services as rpt_support
from app.reports import trends as rpt_trends
from app.reports import result_slips as rpt_slips

router = APIRouter()


# ══════════════════════════════════════════════════════════════════════════════
# STUDENTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/students/list/excel",   summary="Student master list — Excel")
def students_list_excel(academic_year_id: Optional[int] = None,
                        db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_students.student_list_excel(db, academic_year_id)

@router.get("/students/list/pdf",     summary="Student master list — PDF")
def students_list_pdf(academic_year_id: Optional[int] = None,
                      db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_students.student_list_pdf(db, academic_year_id)

@router.get("/students/performance/excel", summary="Student CBC performance — Excel")
def students_performance_excel(academic_year_id: Optional[int] = None,
                                db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_students.student_performance_excel(db, academic_year_id)

@router.get("/students/performance/pdf",   summary="Student CBC performance — PDF")
def students_performance_pdf(academic_year_id: Optional[int] = None,
                              db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_students.student_performance_pdf(db, academic_year_id)

@router.get("/students/attendance/excel",  summary="Student attendance — Excel")
def students_attendance_excel(academic_year_id: Optional[int] = None,
                               threshold: float = Query(75.0),
                               db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_students.student_attendance_excel(db, academic_year_id, threshold)

@router.get("/students/health/excel",      summary="Student health records — Excel")
def students_health_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_students.student_health_excel(db)

@router.get("/students/health/pdf",        summary="Student health records — PDF")
def students_health_pdf(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_students.student_health_pdf(db)


# ══════════════════════════════════════════════════════════════════════════════
# STAFF
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/staff/teachers/excel",   summary="Teacher directory — Excel")
def teachers_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_staff.teacher_list_excel(db)

@router.get("/staff/teachers/pdf",     summary="Teacher directory — PDF")
def teachers_pdf(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_staff.teacher_list_pdf(db)

@router.get("/staff/profiles/excel",   summary="Staff HR profiles — Excel")
def staff_profiles_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_staff.staff_profiles_excel(db)

@router.get("/staff/tpad/excel",       summary="TPAD appraisals — Excel")
def tpad_excel(academic_year_id: Optional[int] = None,
               db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_staff.tpad_report_excel(db, academic_year_id)

@router.get("/staff/tpad/pdf",         summary="TPAD appraisals — PDF")
def tpad_pdf(academic_year_id: Optional[int] = None,
             db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_staff.tpad_report_pdf(db, academic_year_id)

@router.get("/staff/leave/excel",      summary="Staff leave requests — Excel")
def leave_excel(academic_year_id: Optional[int] = None,
                db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_staff.leave_report_excel(db, academic_year_id)

@router.get("/staff/payroll/excel",    summary="Payroll report — Excel")
def payroll_excel(payroll_run_id: Optional[int] = None,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = rpt_staff.payroll_report_excel(db, payroll_run_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(404, "No payroll run found")
    return result

@router.get("/staff/payroll/pdf",      summary="Payroll report — PDF")
def payroll_pdf(payroll_run_id: Optional[int] = None,
                db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = rpt_staff.payroll_report_pdf(db, payroll_run_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(404, "No payroll run found")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# FINANCE
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/finance/fees/excel",         summary="Fee collection — Excel")
def fees_excel(academic_year_id: Optional[int] = None,
               db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_finance.fee_collection_excel(db, academic_year_id)

@router.get("/finance/fees/pdf",           summary="Fee collection summary — PDF")
def fees_pdf(academic_year_id: Optional[int] = None,
             db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_finance.fee_collection_pdf(db, academic_year_id)

@router.get("/finance/outstanding/excel",  summary="Outstanding fee balances — Excel")
def outstanding_excel(academic_year_id: Optional[int] = None,
                      db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_finance.outstanding_fees_excel(db, academic_year_id)

@router.get("/finance/payment-methods/excel", summary="Payment methods breakdown — Excel")
def payment_methods_excel(academic_year_id: Optional[int] = None,
                           db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_finance.payment_methods_excel(db, academic_year_id)


# ══════════════════════════════════════════════════════════════════════════════
# ACADEMIC
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/academic/exams/excel",         summary="Exam results — Excel")
def exams_excel(exam_session_id: Optional[int] = None,
                db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_academic.exam_results_excel(db, exam_session_id)

@router.get("/academic/exams/pdf",           summary="Exam results — PDF")
def exams_pdf(exam_session_id: Optional[int] = None,
              db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_academic.exam_results_pdf(db, exam_session_id)

@router.get("/academic/report-cards/excel",  summary="CBC report cards — Excel")
def report_cards_excel(academic_year_id: Optional[int] = None,
                       db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_academic.report_cards_excel(db, academic_year_id)

@router.get("/academic/lms-submissions/excel", summary="LMS assignment submissions — Excel")
def lms_submissions_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_academic.lms_submissions_excel(db)

@router.get("/academic/quiz-attempts/excel",   summary="Quiz attempt results — Excel")
def quiz_attempts_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_academic.quiz_attempts_excel(db)

@router.get("/academic/lesson-plans/excel",    summary="Lesson plans — Excel")
def lesson_plans_excel(academic_year_id: Optional[int] = None,
                       db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_academic.lesson_plans_excel(db, academic_year_id)


# ══════════════════════════════════════════════════════════════════════════════
# LIBRARY
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/library/catalogue/excel",   summary="Library catalogue — Excel")
def library_catalogue_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_support.library_catalogue_excel(db)

@router.get("/library/movements/excel",   summary="Borrowing records — Excel")
def library_movements_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_support.library_movements_excel(db)

@router.get("/library/overdue/pdf",       summary="Overdue books — PDF")
def library_overdue_pdf(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_support.library_overdue_pdf(db)


# ══════════════════════════════════════════════════════════════════════════════
# HOSTEL
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/hostel/occupancy/excel",    summary="Hostel room occupancy — Excel")
def hostel_occupancy_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_support.hostel_occupancy_excel(db)

@router.get("/hostel/allocations/excel",  summary="Hostel boarder allocations — Excel")
def hostel_allocations_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_support.hostel_allocations_excel(db)

@router.get("/hostel/allocations/pdf",    summary="Hostel boarder allocations — PDF")
def hostel_allocations_pdf(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_support.hostel_allocations_pdf(db)


# ══════════════════════════════════════════════════════════════════════════════
# TRANSPORT
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/transport/manifest/excel",  summary="Transport route manifest — Excel")
def transport_manifest_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_support.transport_manifest_excel(db)

@router.get("/transport/manifest/pdf",    summary="Transport route manifest — PDF")
def transport_manifest_pdf(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_support.transport_manifest_pdf(db)


# ══════════════════════════════════════════════════════════════════════════════
# HEALTH / CLINIC
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/health/clinic-visits/excel",  summary="Clinic visit records — Excel")
def clinic_visits_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_support.clinic_visits_excel(db)

@router.get("/health/clinic-visits/pdf",    summary="Clinic visit records — PDF")
def clinic_visits_pdf(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_support.clinic_visits_pdf(db)

@router.get("/health/vaccinations/excel",   summary="Vaccination records — Excel")
def vaccinations_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_support.vaccination_report_excel(db)


# ══════════════════════════════════════════════════════════════════════════════
# RESULT SLIPS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/result-slips/student/{student_id}/pdf",
            summary="Comprehensive result slip for one student — PDF")
def result_slip_pdf(student_id: int,
                    academic_year_id: Optional[int] = None,
                    academic_term_id: Optional[int] = None,
                    db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = rpt_slips.student_result_slip_pdf(db, student_id, academic_year_id, academic_term_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Student not found")
    return result


@router.get("/result-slips/bulk/excel",
            summary="Bulk result slips for all students in a grade — Excel (one sheet per student)")
def bulk_result_slips_excel(course_id: Optional[int] = None,
                             academic_year_id: Optional[int] = None,
                             academic_term_id: Optional[int] = None,
                             db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_slips.bulk_result_slips_excel(db, course_id, academic_year_id, academic_term_id)


@router.get("/result-slips/student/{student_id}/progressive/excel",
            summary="Progressive assessment history for one student — Excel (3 sheets)")
def progressive_assessment_excel(student_id: int,
                                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = rpt_slips.progressive_assessment_excel(db, student_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Student not found")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# TRENDS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/trends/attendance/excel",
            summary="Monthly attendance rate trend — Excel (with chart)")
def attendance_trend_excel(academic_year_id: Optional[int] = None,
                            db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_trends.attendance_trend_excel(db, academic_year_id)


@router.get("/trends/attendance/pdf",
            summary="Monthly attendance rate trend — PDF")
def attendance_trend_pdf(academic_year_id: Optional[int] = None,
                          db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_trends.attendance_trend_pdf(db, academic_year_id)


@router.get("/trends/fees/excel",
            summary="Fee collection trend per term — Excel")
def fee_trend_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_trends.fee_collection_trend_excel(db)


@router.get("/trends/fees/pdf",
            summary="Fee collection trend per term — PDF")
def fee_trend_pdf(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_trends.fee_collection_trend_pdf(db)


@router.get("/trends/performance/student/{student_id}/excel",
            summary="Individual student performance progression across all terms — Excel")
def student_progression_excel(student_id: int,
                               db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = rpt_trends.student_performance_progression_excel(db, student_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Student not found")
    return result


@router.get("/trends/cbc-levels/excel",
            summary="School-wide CBC level distribution trend per term — Excel")
def cbc_level_trend_excel(academic_year_id: Optional[int] = None,
                           db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_trends.cbc_level_distribution_trend_excel(db, academic_year_id)


@router.get("/trends/exam-scores/excel",
            summary="Exam average score trend per subject per session — Excel")
def exam_score_trend_excel(academic_year_id: Optional[int] = None,
                            db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_trends.exam_score_trend_excel(db, academic_year_id)


@router.get("/trends/lms-engagement/excel",
            summary="Monthly LMS assignment submissions and quiz attempts — Excel")
def lms_engagement_trend_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_trends.lms_engagement_trend_excel(db)


@router.get("/trends/health-visits/excel",
            summary="Monthly clinic visit trend by type — Excel")
def health_visit_trend_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_trends.health_visit_trend_excel(db)


@router.get("/trends/library-usage/excel",
            summary="Monthly library book issues and returns trend — Excel")
def library_usage_trend_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_trends.library_usage_trend_excel(db)


@router.get("/trends/staff-leave/excel",
            summary="Monthly approved staff leave trend by type — Excel")
def staff_leave_trend_excel(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return rpt_trends.staff_leave_trend_excel(db)
