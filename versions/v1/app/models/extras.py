"""
Remaining modules: Achievement, Activity, Blog, Cafeteria,
Discipline, Event, Facility, Inventory, Lesson, LMS,
Mentorship, NoticeBoard, Scholarship, DigiGuide
"""
import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    ForeignKey, Float, Text, Enum, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

# ── Association tables ────────────────────────────────────────────────────────
mentorship_students = Table("mentorship_students", Base.metadata,
    Column("group_id", Integer, ForeignKey("mentorship_groups.id", ondelete="CASCADE")),
    Column("student_id", Integer, ForeignKey("students.id", ondelete="CASCADE")),
)


# ── Achievement ───────────────────────────────────────────────────────────────
class AchievementType(Base):
    __tablename__ = "achievement_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)


class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    achievement_type_id = Column(Integer, ForeignKey("achievement_types.id"))
    title = Column(String(200), nullable=False)
    date = Column(Date)
    description = Column(Text)
    certificate_number = Column(String(100))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    achievement_type = relationship("AchievementType")


# ── Activity ──────────────────────────────────────────────────────────────────
class ActivityType(Base):
    __tablename__ = "activity_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_type_id = Column(Integer, ForeignKey("activity_types.id"))
    name = Column(String(200), nullable=False)
    date = Column(Date)
    description = Column(Text)
    status = Column(String(20), default="active")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    activity_type = relationship("ActivityType")


# ── Blog ──────────────────────────────────────────────────────────────────────
class BlogCategory(Base):
    __tablename__ = "blog_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    posts = relationship("BlogPost", back_populates="category")


class BlogPost(Base):
    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("blog_categories.id"))
    published = Column(Boolean, default=False)
    published_date = Column(DateTime)
    grade_level = Column(String(20))
    image = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("User")
    category = relationship("BlogCategory", back_populates="posts")
    comments = relationship("BlogComment", back_populates="post", cascade="all, delete-orphan")


class BlogComment(Base):
    __tablename__ = "blog_comments"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("blog_posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("BlogPost", back_populates="comments")
    author = relationship("User")


# ── Cafeteria ─────────────────────────────────────────────────────────────────
class FoodCategory(Base):
    __tablename__ = "food_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    items = relationship("MenuItem", back_populates="category")


class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("food_categories.id"))
    price = Column(Float)
    description = Column(Text)
    active = Column(Boolean, default=True)

    category = relationship("FoodCategory", back_populates="items")


class DailyMenu(Base):
    __tablename__ = "daily_menus"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, unique=True)
    description = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Discipline ────────────────────────────────────────────────────────────────
class DisciplineAction(Base):
    __tablename__ = "discipline_actions"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)


class Discipline(Base):
    __tablename__ = "discipline_records"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    action_id = Column(Integer, ForeignKey("discipline_actions.id"))
    severity = Column(String(20), default="minor")   # minor | moderate | severe
    reported_by = Column(Integer, ForeignKey("users.id"))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    action = relationship("DisciplineAction")


# ── Event ─────────────────────────────────────────────────────────────────────
class EventType(Base):
    __tablename__ = "event_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    event_type_id = Column(Integer, ForeignKey("event_types.id"))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    location = Column(String(300))
    description = Column(Text)
    max_participants = Column(Integer)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    event_type = relationship("EventType")
    registrations = relationship("EventRegistration", back_populates="event",
                                 cascade="all, delete-orphan")


class EventRegistration(Base):
    __tablename__ = "event_registrations"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    registration_date = Column(DateTime, server_default=func.now())
    status = Column(String(20), default="registered")   # registered | attended | cancelled

    event = relationship("Event", back_populates="registrations")
    student = relationship("Student")


# ── Facility ──────────────────────────────────────────────────────────────────
class Facility(Base):
    __tablename__ = "facilities"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    facility_type = Column(String(100))
    location = Column(String(200))
    capacity = Column(Integer)
    description = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Inventory ─────────────────────────────────────────────────────────────────
class InventoryCategory(Base):
    __tablename__ = "inventory_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    items = relationship("InventoryItem", back_populates="category")


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True)
    category_id = Column(Integer, ForeignKey("inventory_categories.id"))
    quantity = Column(Float, default=0)
    unit = Column(String(50))
    unit_price = Column(Float)
    reorder_level = Column(Float)
    description = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("InventoryCategory", back_populates="items")
    transactions = relationship("InventoryTransaction", back_populates="item")


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)   # in | out | adjustment
    quantity = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    reference = Column(String(100))
    note = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("InventoryItem", back_populates="transactions")


# ── Lesson ────────────────────────────────────────────────────────────────────
class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"))
    faculty_id = Column(Integer, ForeignKey("teachers.id"))
    content = Column(Text)
    objectives = Column(Text)
    duration_minutes = Column(Integer)
    week_number = Column(Integer)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subject = relationship("Subject")
    course = relationship("Course")
    faculty = relationship("Teacher")


# ── LMS ───────────────────────────────────────────────────────────────────────
class LMSCourse(Base):
    __tablename__ = "lms_courses"
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    description = Column(Text)
    course_id = Column(Integer, ForeignKey("courses.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    faculty_id = Column(Integer, ForeignKey("teachers.id"))
    thumbnail = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course")
    subject = relationship("Subject")
    faculty = relationship("Teacher")
    sections = relationship("LMSSection", back_populates="lms_course",
                            order_by="LMSSection.sequence", cascade="all, delete-orphan")
    enrollments = relationship("LMSEnrollment", back_populates="lms_course")


class LMSSection(Base):
    __tablename__ = "lms_sections"
    id = Column(Integer, primary_key=True)
    lms_course_id = Column(Integer, ForeignKey("lms_courses.id"), nullable=False)
    name = Column(String(300), nullable=False)
    sequence = Column(Integer, default=1)
    active = Column(Boolean, default=True)

    lms_course = relationship("LMSCourse", back_populates="sections")
    contents = relationship("LMSContent", back_populates="section",
                            order_by="LMSContent.sequence", cascade="all, delete-orphan")


class LMSContent(Base):
    __tablename__ = "lms_contents"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("lms_sections.id"), nullable=False)
    name = Column(String(300), nullable=False)
    content_type = Column(String(50))   # video | pdf | quiz | text | link
    content_url = Column(String)
    content_text = Column(Text)
    duration_minutes = Column(Integer)
    sequence = Column(Integer, default=1)
    active = Column(Boolean, default=True)

    section = relationship("LMSSection", back_populates="contents")


class LMSEnrollment(Base):
    __tablename__ = "lms_enrollments"
    id = Column(Integer, primary_key=True)
    lms_course_id = Column(Integer, ForeignKey("lms_courses.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    enrollment_date = Column(DateTime, server_default=func.now())
    progress_percent = Column(Float, default=0)
    completed = Column(Boolean, default=False)
    completed_date = Column(DateTime)

    lms_course = relationship("LMSCourse", back_populates="enrollments")
    student = relationship("Student")


# ── Mentorship ────────────────────────────────────────────────────────────────
class Mentor(Base):
    __tablename__ = "mentors"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    expertise = Column(String(300))
    bio = Column(Text)
    approved = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    teacher = relationship("Teacher")
    groups = relationship("MentorshipGroup", back_populates="mentor")


class MentorshipGroup(Base):
    __tablename__ = "mentorship_groups"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)
    description = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    mentor = relationship("Mentor", back_populates="groups")
    students = relationship("Student", secondary=mentorship_students)
    messages = relationship("MentorshipMessage", back_populates="group",
                            cascade="all, delete-orphan")


class MentorshipMessage(Base):
    __tablename__ = "mentorship_messages"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("mentorship_groups.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("MentorshipGroup", back_populates="messages")
    sender = relationship("User")


# ── Notice Board ──────────────────────────────────────────────────────────────
class NoticeBoard(Base):
    __tablename__ = "notice_board"
    id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    posted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_audience = Column(String(50), default="all")   # all | students | teachers | parents
    posted_date = Column(DateTime, server_default=func.now())
    expiry_date = Column(DateTime)
    active = Column(Boolean, default=True)

    posted_by_user = relationship("User")


# ── Scholarship ───────────────────────────────────────────────────────────────
class ScholarshipType(Base):
    __tablename__ = "scholarship_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    amount = Column(Float)
    active = Column(Boolean, default=True)


class Scholarship(Base):
    __tablename__ = "scholarships"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    scholarship_type_id = Column(Integer, ForeignKey("scholarship_types.id"), nullable=False)
    amount = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    state = Column(String(20), default="active")   # active | expired | cancelled
    note = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    scholarship_type = relationship("ScholarshipType")
    academic_year = relationship("AcademicYear")


# ── DigiGuide ─────────────────────────────────────────────────────────────────
class AcademicPerformance(Base):
    __tablename__ = "academic_performances"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    academic_term_id = Column(Integer, ForeignKey("academic_terms.id"))
    assignment_score = Column(Float)
    midterm_score = Column(Float)
    final_score = Column(Float)
    total_score = Column(Float)
    grade = Column(String(10))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    subject = relationship("Subject")
    academic_year = relationship("AcademicYear")
    academic_term = relationship("AcademicTerm")


class CareerPath(Base):
    __tablename__ = "career_paths"
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    description = Column(Text)
    min_grade = Column(String(10))
    required_subjects = Column(Text)   # JSON list of subject names
    university_requirements = Column(Text)
    active = Column(Boolean, default=True)


class StudentCareerMatch(Base):
    __tablename__ = "student_career_matches"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    career_id = Column(Integer, ForeignKey("career_paths.id"), nullable=False)
    match_score = Column(Float)
    predicted_grade = Column(String(10))
    recommendation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    career = relationship("CareerPath")


# ── Alumni ────────────────────────────────────────────────────────────────────
class Alumni(Base):
    __tablename__ = "alumni"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, unique=True)
    graduation_year = Column(Integer)
    graduation_date = Column(Date)
    final_grade = Column(String(20))
    current_employer = Column(String(300))
    current_position = Column(String(300))
    linkedin_url = Column(String)
    email = Column(String(200))
    phone = Column(String(20))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
