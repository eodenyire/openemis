# Import all models so SQLAlchemy registers them before create_all
from app.models.user import User  # noqa
from app.models.core import (  # noqa
    OpDepartment, OpProgram, OpAcademicYear, OpAcademicTerm,
    OpCourse, OpSubject, OpBatch, OpCategory, OpStudent, OpFaculty, OpStudentCourse,
)
from app.models.admission import OpAdmissionRegister, OpAdmission  # noqa
from app.models.fees import OpFeesTerms, OpFeesTermsLine, OpFeesElement, OpStudentFeeInvoice, OpFeePayment  # noqa
from app.models.timetable import OpTimetableRoom, OpTiming, OpSession  # noqa
from app.models.attendance import OpAttendanceRegister, OpAttendanceSheet, OpAttendanceLine  # noqa
from app.models.exam import (  # noqa
    OpExamSession, OpExam, OpExamAttendee,
    OpMarksheetRegister, OpMarksheetLine,
)
from app.models.lms import OpLmsCourse, OpLmsSection, OpLmsContent, OpLmsEnrollment  # noqa
from app.models.support import (  # noqa
    OpLibraryBook, OpLibraryMovement,
    OpHostelBlock, OpHostelRoomType, OpHostelRoom, OpHostelAllocation,
    OpHealthRecord,
    OpTransportVehicle, OpTransportRoute, OpTransportRouteStop, OpStudentTransport,
)
from app.models.extras import (  # noqa
    OpActivity, OpAchievement, OpDisciplineRecord,
    OpEvent, OpEventRegistration,
    OpNotice, OpBlogPost,
    OpScholarship, OpScholarshipAward,
    OpAlumni, OpFacility,
)
# ── New OpenEMIS-18.0 models ──────────────────────────────────────────────────
from app.models.cbc import (  # noqa
    CbcStrand, CbcSubstrand, CbcLearningOutcome, CbcRubric,
    IrAttachment, CbcPortfolio, CbcFormativeAssessment,
    CbcReportCard, CbcReportCardLine,
)
from app.models.digiguide import (  # noqa
    OpAcademicPerformance, OpNationalExamPrediction,
    OpKuccpsCareer, OpCareerMatch,
)
from app.models.health import (  # noqa
    OpMedicalCondition, OpVaccination, OpStudentHealth,
)
from app.models.facilities import (  # noqa
    OpClassroom, OpClassroomAsset,
    OpGradingConfig, OpGradingRule,
    OpFoodCategory, OpMenuItem, OpDailyMenu,
    OpInventoryCategory, OpInventoryItem, OpInventoryTransaction,
    OpLesson,
    OpParentRelationship, OpParent,
    OpMentor, OpMentorshipGroup, OpMentorshipMessage,
)
