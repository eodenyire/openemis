from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, students, users, people, core,
    admission, fees, attendance, exam, assignment, library, timetable,
    hostel, transport, extras, cbc, dashboard,
    payments, tenants, lifecycle, finance,
)
from app.api.v1.endpoints import lms, lesson_plans, timetable_v2
from app.api.v1.endpoints import hr, leave, tpad, payroll
from app.api.v1.endpoints import sms, announcements, parent_portal
from app.api.v1.endpoints import library_v2, hostel_v2, transport_v2, health
from app.api.v1.endpoints import analytics, early_warning, nemis, knec, government
from app.api.v1.endpoints import reports
from app.api.v1.endpoints import (
    discipline, events, inventory, cafeteria, achievements,
    scholarships, alumni, mentorship, noticeboard, digiguide, facilities,
    teacher_portal, student_portal,
    activities, blog,
)

api_router = APIRouter()

# ── Core ──────────────────────────────────────────────────────────────────────
api_router.include_router(auth.router,          prefix="/auth",           tags=["Authentication"])
api_router.include_router(users.router,         prefix="/users",          tags=["Users"])
api_router.include_router(students.router,      prefix="/students",       tags=["Students"])
api_router.include_router(people.router,        prefix="/people",         tags=["People"])
api_router.include_router(core.router,          prefix="/core",           tags=["Core"])
api_router.include_router(admission.router,     prefix="/admissions",     tags=["Admission"])
api_router.include_router(fees.router,          prefix="/fees",           tags=["Fees"])
api_router.include_router(attendance.router,    prefix="/attendance",     tags=["Attendance"])
api_router.include_router(exam.router,          prefix="/exams",          tags=["Exams"])
api_router.include_router(assignment.router,    prefix="/assignments",    tags=["Assignments"])
api_router.include_router(library.router,       prefix="/library",        tags=["Library"])
api_router.include_router(timetable.router,     prefix="/timetable",      tags=["Timetable"])
api_router.include_router(hostel.router,        prefix="/hostel",         tags=["Hostel"])
api_router.include_router(transport.router,     prefix="/transport",      tags=["Transport"])
api_router.include_router(extras.router,        prefix="/extras",         tags=["Extras"])
api_router.include_router(cbc.router,           prefix="/cbc",            tags=["CBC Curriculum"])
api_router.include_router(dashboard.router,     prefix="/dashboard",      tags=["Dashboard"])
api_router.include_router(payments.router,      prefix="/payments",       tags=["Payments / M-Pesa"])
api_router.include_router(tenants.router,       prefix="/tenants",        tags=["Tenants"])
api_router.include_router(lifecycle.router,     prefix="/lifecycle",      tags=["Student Lifecycle"])
api_router.include_router(finance.router,       prefix="/finance",        tags=["Finance"])

# ── Academic & LMS ────────────────────────────────────────────────────────────
api_router.include_router(lms.router,           prefix="/lms",            tags=["LMS / Digital Classroom"])
api_router.include_router(lesson_plans.router,  prefix="/lesson-plans",   tags=["Lesson Planning"])
api_router.include_router(timetable_v2.router,  prefix="/timetable",      tags=["Timetable v2"])

# ── HR ────────────────────────────────────────────────────────────────────────
api_router.include_router(hr.router,            prefix="/hr",             tags=["HR / Staff"])
api_router.include_router(leave.router,         prefix="/leave",          tags=["Leave Management"])
api_router.include_router(tpad.router,          prefix="/tpad",           tags=["TPAD Appraisal"])
api_router.include_router(payroll.router,       prefix="/payroll",        tags=["Payroll"])

# ── Communications ────────────────────────────────────────────────────────────
api_router.include_router(sms.router,           prefix="/sms",            tags=["SMS"])
api_router.include_router(announcements.router, prefix="/announcements",  tags=["Announcements"])
api_router.include_router(parent_portal.router, prefix="/parent",         tags=["Parent Portal"])

# ── Support Services ──────────────────────────────────────────────────────────
api_router.include_router(library_v2.router,    prefix="/library",        tags=["Library"])
api_router.include_router(hostel_v2.router,     prefix="/hostel",         tags=["Hostel"])
api_router.include_router(transport_v2.router,  prefix="/transport",      tags=["Transport"])
api_router.include_router(health.router,        prefix="/health",         tags=["Health"])

# ── Analytics & Government ────────────────────────────────────────────────────
api_router.include_router(analytics.router,     prefix="/analytics",      tags=["Analytics"])
api_router.include_router(early_warning.router, prefix="/early-warning",  tags=["AI Early Warning"])
api_router.include_router(nemis.router,         prefix="/nemis",          tags=["NEMIS"])
api_router.include_router(knec.router,          prefix="/knec",           tags=["KNEC"])
api_router.include_router(government.router,    prefix="/government",     tags=["Government Dashboard"])

# ── Reports ───────────────────────────────────────────────────────────────────
api_router.include_router(reports.router,       prefix="/reports",        tags=["Reports (Excel/PDF)"])

# ── Gap-fill modules ──────────────────────────────────────────────────────────
api_router.include_router(discipline.router,    prefix="/discipline",     tags=["Discipline"])
api_router.include_router(events.router,        prefix="/events",         tags=["Events & Calendar"])
api_router.include_router(inventory.router,     prefix="/inventory",      tags=["Inventory"])
api_router.include_router(cafeteria.router,     prefix="/cafeteria",      tags=["Cafeteria"])
api_router.include_router(achievements.router,  prefix="/achievements",   tags=["Achievements & Activities"])
api_router.include_router(scholarships.router,  prefix="/scholarships",   tags=["Scholarships"])
api_router.include_router(alumni.router,        prefix="/alumni",         tags=["Alumni"])
api_router.include_router(mentorship.router,    prefix="/mentorship",     tags=["Mentorship"])
api_router.include_router(noticeboard.router,   prefix="/noticeboard",    tags=["Notice Board & Blog"])
api_router.include_router(blog.router,          prefix="/blog",           tags=["Blog"])
api_router.include_router(activities.router,    prefix="/activities",     tags=["Activities"])
api_router.include_router(digiguide.router,     prefix="/digiguide",      tags=["DigiGuide / Career Guidance"])
api_router.include_router(facilities.router,    prefix="/facilities",     tags=["Facilities"])

# ── Role Portals ──────────────────────────────────────────────────────────────
api_router.include_router(teacher_portal.router, prefix="/teacher",       tags=["Teacher Portal"])
api_router.include_router(student_portal.router, prefix="/student",       tags=["Student Portal"])
