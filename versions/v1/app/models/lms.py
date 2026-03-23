"""LMS + Lesson Planning models — Digital Classroom (Canvas/Moodle-inspired)."""
import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    ForeignKey, Text, Enum, Float, Time
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


# ── Enums ─────────────────────────────────────────────────────────────────────

class LessonPlanStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class ResourceType(str, enum.Enum):
    PDF = "pdf"
    VIDEO = "video"
    LINK = "link"
    IMAGE = "image"
    DOCUMENT = "document"
    OTHER = "other"


class QuizQuestionType(str, enum.Enum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"


class AssignmentSubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    LATE = "late"
    GRADED = "graded"
    RETURNED = "returned"


class VirtualClassStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    ENDED = "ended"
    CANCELLED = "cancelled"


# ── Lesson Planning ───────────────────────────────────────────────────────────

class SchemeOfWork(Base):
    """Term-long teaching plan per subject per class."""
    __tablename__ = "schemes_of_work"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    academic_term_id = Column(Integer, ForeignKey("academic_terms.id"), nullable=False)
    status = Column(Enum(LessonPlanStatus), default=LessonPlanStatus.DRAFT)
    approved_by_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course")
    subject = relationship("Subject")
    teacher = relationship("Teacher", foreign_keys=[teacher_id])
    lesson_plans = relationship("LessonPlan", back_populates="scheme")


class LessonPlan(Base):
    """Individual lesson plan linked to a SubStrand and SchemeOfWork."""
    __tablename__ = "lesson_plans"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes_of_work.id"), nullable=False)
    title = Column(String(200), nullable=False)
    week_number = Column(Integer, nullable=False)
    lesson_number = Column(Integer, default=1)
    sub_strand_id = Column(Integer, ForeignKey("sub_strands.id"), nullable=True)
    objectives = Column(Text)
    activities = Column(Text)
    resources_needed = Column(Text)
    assessment_method = Column(Text)
    duration_minutes = Column(Integer, default=40)
    status = Column(Enum(LessonPlanStatus), default=LessonPlanStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    scheme = relationship("SchemeOfWork", back_populates="lesson_plans")
    sub_strand = relationship("SubStrand")


class TeachingResource(Base):
    """Uploaded teaching materials — PDFs, videos, links."""
    __tablename__ = "teaching_resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    resource_type = Column(Enum(ResourceType), default=ResourceType.DOCUMENT)
    url = Column(String(500))
    file_path = Column(String(500))
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    uploaded_by_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subject = relationship("Subject")
    uploaded_by = relationship("Teacher")


# ── Virtual Classroom (LMS) ───────────────────────────────────────────────────

class VirtualClassroom(Base):
    """A digital class space — students enroll, teacher posts content."""
    __tablename__ = "virtual_classrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    academic_term_id = Column(Integer, ForeignKey("academic_terms.id"), nullable=False)
    join_code = Column(String(10), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course")
    subject = relationship("Subject")
    teacher = relationship("Teacher")
    enrollments = relationship("VirtualClassEnrollment", back_populates="classroom")
    posts = relationship("ClassPost", back_populates="classroom")
    assignments = relationship("ClassAssignment", back_populates="classroom")
    quizzes = relationship("Quiz", back_populates="classroom")


class VirtualClassEnrollment(Base):
    """Student enrolled in a virtual classroom."""
    __tablename__ = "virtual_class_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("virtual_classrooms.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    classroom = relationship("VirtualClassroom", back_populates="enrollments")


class ClassPost(Base):
    """Announcement / lesson content posted in a virtual classroom."""
    __tablename__ = "class_posts"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("virtual_classrooms.id"), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text)
    resource_url = Column(String(500))
    resource_type = Column(Enum(ResourceType), nullable=True)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    classroom = relationship("VirtualClassroom", back_populates="posts")
    comments = relationship("PostComment", back_populates="post")


class PostComment(Base):
    """Student/teacher comment on a class post."""
    __tablename__ = "post_comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("class_posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("ClassPost", back_populates="comments")


# ── Online Assignments ────────────────────────────────────────────────────────

class ClassAssignment(Base):
    """Online assignment posted in a virtual classroom."""
    __tablename__ = "class_assignments"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("virtual_classrooms.id"), nullable=False)
    title = Column(String(200), nullable=False)
    instructions = Column(Text)
    total_marks = Column(Float, default=100)
    due_date = Column(DateTime(timezone=True), nullable=False)
    allow_late = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    classroom = relationship("VirtualClassroom", back_populates="assignments")
    submissions = relationship("ClassAssignmentSubmission", back_populates="assignment")


class ClassAssignmentSubmission(Base):
    """Student submission for a class assignment."""
    __tablename__ = "class_assignment_submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("class_assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    submission_text = Column(Text)
    file_url = Column(String(500))
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(AssignmentSubmissionStatus), default=AssignmentSubmissionStatus.SUBMITTED)
    marks_obtained = Column(Float, nullable=True)
    feedback = Column(Text)
    graded_at = Column(DateTime(timezone=True), nullable=True)

    assignment = relationship("ClassAssignment", back_populates="submissions")


# ── Quiz Engine ───────────────────────────────────────────────────────────────

class Quiz(Base):
    """Online quiz in a virtual classroom."""
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("virtual_classrooms.id"), nullable=False)
    title = Column(String(200), nullable=False)
    instructions = Column(Text)
    total_marks = Column(Float, default=0)
    duration_minutes = Column(Integer, default=30)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    is_published = Column(Boolean, default=False)
    shuffle_questions = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    classroom = relationship("VirtualClassroom", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz")
    attempts = relationship("QuizAttempt", back_populates="quiz")


class QuizQuestion(Base):
    """A question in a quiz."""
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuizQuestionType), default=QuizQuestionType.MCQ)
    marks = Column(Float, default=1)
    order = Column(Integer, default=1)
    # For MCQ: store options as JSON string
    options = Column(Text)          # JSON: ["Option A", "Option B", ...]
    correct_answer = Column(Text)   # For MCQ: index or text; for T/F: "true"/"false"
    explanation = Column(Text)

    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    """A student's attempt at a quiz."""
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    score = Column(Float, nullable=True)
    answers = Column(Text)   # JSON: {question_id: answer}
    is_submitted = Column(Boolean, default=False)

    quiz = relationship("Quiz", back_populates="attempts")


# ── Timetable Slot (enhanced) ─────────────────────────────────────────────────

class TimetableSlot(Base):
    """
    Weekly recurring timetable slot — replaces ad-hoc Session for structured scheduling.
    Constraint: no teacher double-booking, no room double-booking per day+period.
    """
    __tablename__ = "timetable_slots"

    id = Column(Integer, primary_key=True, index=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    academic_term_id = Column(Integer, ForeignKey("academic_terms.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)
    timing_id = Column(Integer, ForeignKey("timings.id"), nullable=False)
    day_of_week = Column(String(10), nullable=False)   # monday…friday
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    academic_year = relationship("AcademicYear")
    academic_term = relationship("AcademicTerm")
    course = relationship("Course")
    batch = relationship("Batch")
    subject = relationship("Subject")
    teacher = relationship("Teacher")
    classroom = relationship("Classroom")
    timing = relationship("Timing")


# ── Academic Calendar ─────────────────────────────────────────────────────────

class CalendarEventType(str, enum.Enum):
    HOLIDAY = "holiday"
    EXAM = "exam"
    SPORTS = "sports"
    MEETING = "meeting"
    TRIP = "trip"
    OTHER = "other"


class AcademicCalendarEvent(Base):
    """School calendar events — holidays, sports days, parent meetings."""
    __tablename__ = "academic_calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    event_type = Column(Enum(CalendarEventType), default=CalendarEventType.OTHER)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_school_wide = Column(Boolean, default=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    academic_year = relationship("AcademicYear")
