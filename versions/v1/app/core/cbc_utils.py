"""CBC utility functions."""
from app.models.cbc import PerformanceLevel


def score_to_cbc_level(score: float) -> PerformanceLevel:
    """Convert a raw percentage score to a CBC performance level."""
    if score >= 80:
        return PerformanceLevel.EE
    elif score >= 60:
        return PerformanceLevel.ME
    elif score >= 40:
        return PerformanceLevel.AE
    else:
        return PerformanceLevel.BE


# Default permissions per role: resource:action:scope
ROLE_PERMISSIONS: dict[str, list[str]] = {
    "super_admin": ["*:*:system"],
    "school_admin": [
        "students:read:school", "students:write:school",
        "teachers:read:school", "teachers:write:school",
        "fees:read:school", "fees:write:school",
        "attendance:read:school", "exams:read:school",
        "reports:read:school", "reports:write:school",
        "users:read:school", "users:write:school",
        "timetable:read:school", "timetable:write:school",
        "hr:read:school", "hr:write:school",
        "analytics:read:school",
    ],
    "academic_director": [
        "students:read:school", "teachers:read:school",
        "timetable:read:school", "timetable:write:school",
        "exams:read:school", "exams:write:school",
        "attendance:read:school", "reports:read:school",
        "cbc:read:school", "cbc:write:school",
    ],
    "teacher": [
        "students:read:class", "attendance:write:class",
        "exams:write:class", "assignments:write:class",
        "reports:write:class", "cbc:write:class",
        "timetable:read:own", "messages:write:own",
    ],
    "student": [
        "timetable:read:own", "assignments:read:own",
        "exams:read:own", "attendance:read:own",
        "reports:read:own", "library:read:school",
    ],
    "parent": [
        "students:read:own", "attendance:read:own",
        "fees:read:own", "fees:write:own",
        "exams:read:own", "reports:read:own",
        "messages:write:own",
    ],
    "finance_officer": [
        "fees:read:school", "fees:write:school",
        "payments:read:school", "payments:write:school",
        "payroll:read:school", "reports:read:school",
    ],
    "registrar": [
        "students:read:school", "students:write:school",
        "admissions:read:school", "admissions:write:school",
        "transfers:read:school", "transfers:write:school",
    ],
    "librarian": [
        "library:read:school", "library:write:school",
        "students:read:school",
    ],
    "transport_manager": [
        "transport:read:school", "transport:write:school",
        "students:read:school",
    ],
    "hr_manager": [
        "hr:read:school", "hr:write:school",
        "payroll:read:school", "payroll:write:school",
        "teachers:read:school",
    ],
    "nurse": [
        "health:read:school", "health:write:school",
        "students:read:school",
    ],
    "hostel_manager": [
        "hostel:read:school", "hostel:write:school",
        "students:read:school",
    ],
    "security_officer": [
        "visitors:read:school", "visitors:write:school",
        "students:read:school",
    ],
    "government": [
        "analytics:read:system", "reports:read:system",
        "students:read:system",
    ],
}
