"""
Import all models here so SQLAlchemy registers every table.
This module must be imported before Base.metadata.create_all() is called.
"""
from app.models.user import User, Permission, RolePermission  # noqa: F401
from app.models.core import (                             # noqa: F401
    ProgramLevel, Department, Program, Course, Batch,
    Subject, AcademicYear, AcademicTerm, StudentCategory,
)
from app.models.people import (                           # noqa: F401
    Teacher, Student, StudentCourse, ParentRelationship, Parent,
)
from app.models.admission import Admission, AdmissionRegister  # noqa: F401
from app.models.attendance import (                       # noqa: F401
    AttendanceRegister, AttendanceSheet, AttendanceLine,
)
from app.models.exam import (                             # noqa: F401
    ExamSession, Exam, ExamAttendees, GradingConfig, GradingRule,
)
from app.models.assignment import Assignment, AssignmentSubmission  # noqa: F401
from app.models.timetable import Timing, Classroom, Session  # noqa: F401
from app.models.fees import (                             # noqa: F401
    FeesTerm, FeesTermLine, FeesElement, StudentFeeInvoice, FeePayment,
)
from app.models.library import (                          # noqa: F401
    MediaType, Author, Publisher, LibraryTag, Media, MediaMovement,
)
from app.models.hostel import (                           # noqa: F401
    HostelBlock, HostelRoomType, HostelRoom, HostelAllocation,
)
from app.models.transportation import (                   # noqa: F401
    Vehicle, TransportRoute, TransportRouteStop, StudentTransport,
)
from app.models.health import (                           # noqa: F401
    MedicalCondition, Vaccination, StudentHealth,
    ClinicVisit, VaccinationRecord,
)
from app.models.extras import (                           # noqa: F401
    AchievementType, Achievement,
    ActivityType, Activity,
    BlogCategory, BlogPost, BlogComment,
    FoodCategory, MenuItem, DailyMenu,
    DisciplineAction, Discipline,
    EventType, Event, EventRegistration,
    Facility,
    InventoryCategory, InventoryItem, InventoryTransaction,
    Lesson,
    LMSCourse, LMSSection, LMSContent, LMSEnrollment,
    Mentor, MentorshipGroup, MentorshipMessage,
    NoticeBoard,
    ScholarshipType, Scholarship,
    AcademicPerformance, CareerPath, StudentCareerMatch,
)
from app.models.student_lifecycle import StudentTransfer, PromotionBatch, Alumni  # noqa: F401
from app.models.cbc import (                              # noqa: F401
    CBCGradeLevel, LearningArea, Strand, SubStrand, CompetencyIndicator,
    CBCAssessment, CompetencyScore, ReportCard, ReportCardLine,
)
from app.models.tenant import TenantGroup, Tenant         # noqa: F401
from app.models.mpesa import MpesaTransaction             # noqa: F401
from app.models.lms import (                              # noqa: F401
    SchemeOfWork, LessonPlan, TeachingResource,
    VirtualClassroom, VirtualClassEnrollment, ClassPost, PostComment,
    ClassAssignment, ClassAssignmentSubmission,
    Quiz, QuizQuestion, QuizAttempt,
    TimetableSlot, AcademicCalendarEvent,
)
from app.models.hr import (                               # noqa: F401
    StaffProfile, LeavePolicy, LeaveBalance, LeaveRequest,
    TPADAppraisal, PayComponent, PayrollRun, Payslip, PayslipLine,
)
from app.models.communications import (                   # noqa: F401
    SMSTemplate, SMSBatch, SMSLog,
    Announcement, AnnouncementRead,
    ParentMessage, ParentMessageReply, ParentNotification,
)
