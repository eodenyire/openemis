"""v2 API router — registers all endpoint modules."""
from fastapi import APIRouter

from app.api.v2.endpoints import (
    auth, core, admission, fees, timetable, attendance,
    exam, lms, library, hostel, health, transport,
    activities, events, noticeboard, scholarships,
    mentorship, alumni, facilities, digiguide,
)

api_router = APIRouter()

api_router.include_router(auth.router,         prefix="/auth",         tags=["Auth"])
api_router.include_router(core.router,         prefix="/core",         tags=["Core"])
api_router.include_router(admission.router,    prefix="/admission",    tags=["Admission"])
api_router.include_router(fees.router,         prefix="/fees",         tags=["Fees"])
api_router.include_router(timetable.router,    prefix="/timetable",    tags=["Timetable"])
api_router.include_router(attendance.router,   prefix="/attendance",   tags=["Attendance"])
api_router.include_router(exam.router,         prefix="/exam",         tags=["Exam"])
api_router.include_router(lms.router,          prefix="",              tags=["LMS"])
api_router.include_router(library.router,      prefix="",              tags=["Library"])
api_router.include_router(hostel.router,       prefix="",              tags=["Hostel"])
api_router.include_router(health.router,       prefix="",              tags=["Health"])
api_router.include_router(transport.router,    prefix="",              tags=["Transport"])
api_router.include_router(activities.router,   prefix="/extras",       tags=["Activities"])
api_router.include_router(events.router,       prefix="/extras",       tags=["Events"])
api_router.include_router(noticeboard.router,  prefix="/extras",       tags=["Noticeboard"])
api_router.include_router(scholarships.router, prefix="/extras",       tags=["Scholarships"])
api_router.include_router(mentorship.router,   prefix="/extras",       tags=["Mentorship"])
api_router.include_router(alumni.router,       prefix="/extras",       tags=["Alumni"])
api_router.include_router(facilities.router,   prefix="/extras",       tags=["Facilities"])
api_router.include_router(digiguide.router,    prefix="/extras",       tags=["DigiGuide"])
