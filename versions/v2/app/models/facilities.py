"""Facilities, Classroom, Cafeteria, Inventory, Grading, Lesson, Parent, Mentorship models."""
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Float, Text, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


# ── Association tables ────────────────────────────────────────────────────────

daily_menu_item_rel = Table(
    "op_daily_menu_item_rel", Base.metadata,
    Column("menu_id", Integer, ForeignKey("op_daily_menus.id"), primary_key=True),
    Column("item_id", Integer, ForeignKey("op_menu_items.id"), primary_key=True),
)

mentorship_group_mentor_rel = Table(
    "op_mentorship_group_mentor_rel", Base.metadata,
    Column("group_id", Integer, ForeignKey("op_mentorship_groups.id"), primary_key=True),
    Column("mentor_id", Integer, ForeignKey("op_mentors.id"), primary_key=True),
)

mentorship_group_student_rel = Table(
    "op_mentorship_group_student_rel", Base.metadata,
    Column("group_id", Integer, ForeignKey("op_mentorship_groups.id"), primary_key=True),
    Column("student_id", Integer, ForeignKey("op_students.id"), primary_key=True),
)

mentorship_group_subject_rel = Table(
    "op_mentorship_group_subject_rel", Base.metadata,
    Column("group_id", Integer, ForeignKey("op_mentorship_groups.id"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("op_subjects.id"), primary_key=True),
)

mentor_subject_rel = Table(
    "op_mentor_subject_rel", Base.metadata,
    Column("mentor_id", Integer, ForeignKey("op_mentors.id"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("op_subjects.id"), primary_key=True),
)

parent_student_rel = Table(
    "op_parent_student_rel", Base.metadata,
    Column("parent_id", Integer, ForeignKey("op_parents.id"), primary_key=True),
    Column("student_id", Integer, ForeignKey("op_students.id"), primary_key=True),
)


# ── Classroom ─────────────────────────────────────────────────────────────────

class OpClassroom(Base):
    __tablename__ = "op_classrooms"
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)
    code = Column(String(16), nullable=False, unique=True)
    course_id = Column(Integer, ForeignKey("op_courses.id"))
    batch_id = Column(Integer, ForeignKey("op_batches.id"))
    capacity = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)
    course = relationship("OpCourse")
    batch = relationship("OpBatch")


class OpClassroomAsset(Base):
    __tablename__ = "op_classroom_assets"
    id = Column(Integer, primary_key=True)
    classroom_id = Column(Integer, ForeignKey("op_classrooms.id"))
    product_name = Column(String(256), nullable=False)
    code = Column(String(256))
    quantity = Column(Float, nullable=False)
    classroom = relationship("OpClassroom")


# ── Grading ───────────────────────────────────────────────────────────────────

class OpGradingConfig(Base):
    __tablename__ = "op_grading_configs"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    active = Column(Boolean, default=True)
    rules = relationship("OpGradingRule", back_populates="grading_config")


class OpGradingRule(Base):
    __tablename__ = "op_grading_rules"
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)  # grade label e.g. A, B+
    min_marks = Column(Float, nullable=False)
    max_marks = Column(Float, nullable=False)
    gpa_point = Column(Float, default=0.0)
    grading_config_id = Column(Integer, ForeignKey("op_grading_configs.id"))
    description = Column(String(256))
    active = Column(Boolean, default=True)
    grading_config = relationship("OpGradingConfig", back_populates="rules")


# ── Cafeteria ─────────────────────────────────────────────────────────────────

class OpFoodCategory(Base):
    __tablename__ = "op_food_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    active = Column(Boolean, default=True)


class OpMenuItem(Base):
    __tablename__ = "op_menu_items"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    food_category_id = Column(Integer, ForeignKey("op_food_categories.id"), nullable=False)
    description = Column(Text)
    price = Column(Float, default=0.0)
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    calories = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    food_category = relationship("OpFoodCategory")


class OpDailyMenu(Base):
    __tablename__ = "op_daily_menus"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    date = Column(Date, nullable=False)
    meal_type = Column(String(16), nullable=False)  # breakfast, lunch, dinner, snack
    special_note = Column(Text)
    active = Column(Boolean, default=True)
    __table_args__ = (
        UniqueConstraint("date", "meal_type", name="uq_daily_menu_date_meal"),
    )
    menu_items = relationship("OpMenuItem", secondary=daily_menu_item_rel)


# ── Inventory ─────────────────────────────────────────────────────────────────

class OpInventoryCategory(Base):
    __tablename__ = "op_inventory_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(Text)
    active = Column(Boolean, default=True)


class OpInventoryItem(Base):
    __tablename__ = "op_inventory_items"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    code = Column(String(16), nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey("op_inventory_categories.id"), nullable=False)
    description = Column(Text)
    unit_of_measure = Column(String(32))
    current_stock = Column(Float, default=0.0)
    min_stock_level = Column(Float, default=0.0)
    unit_price = Column(Float, default=0.0)
    low_stock = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    category = relationship("OpInventoryCategory")
    transactions = relationship("OpInventoryTransaction", back_populates="item")


class OpInventoryTransaction(Base):
    __tablename__ = "op_inventory_transactions"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("op_inventory_items.id"), nullable=False)
    transaction_type = Column(String(4), nullable=False)  # in, out
    quantity = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    department_id = Column(Integer, ForeignKey("op_departments.id"))
    reference = Column(String(64))
    notes = Column(Text)
    active = Column(Boolean, default=True)
    item = relationship("OpInventoryItem", back_populates="transactions")


# ── Lesson Plans ──────────────────────────────────────────────────────────────

class OpLesson(Base):
    __tablename__ = "op_lessons"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    faculty_id = Column(Integer, ForeignKey("op_faculty.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("op_courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("op_batches.id"))
    subject_id = Column(Integer, ForeignKey("op_subjects.id"), nullable=False)
    academic_term_id = Column(Integer, ForeignKey("op_academic_terms.id"))
    lesson_date = Column(Date, nullable=False)
    duration = Column(Float, default=0.0)
    lesson_number = Column(Integer, default=0)
    topic = Column(String(256), nullable=False)
    learning_objectives = Column(Text)
    teaching_materials = Column(Text)
    teaching_method = Column(String(16), default="lecture")
    content = Column(Text)
    homework = Column(Text)
    state = Column(String(16), default="draft")  # draft, planned, completed
    notes = Column(Text)
    active = Column(Boolean, default=True)
    faculty = relationship("OpFaculty")
    course = relationship("OpCourse")
    subject = relationship("OpSubject")


# ── Parent ────────────────────────────────────────────────────────────────────

class OpParentRelationship(Base):
    __tablename__ = "op_parent_relationships"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)


class OpParent(Base):
    __tablename__ = "op_parents"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    mobile = Column(String(20))
    email = Column(String(128))
    relationship_id = Column(Integer, ForeignKey("op_parent_relationships.id"), nullable=False)
    active = Column(Boolean, default=True)
    relationship = relationship("OpParentRelationship")
    students = relationship("OpStudent", secondary=parent_student_rel)


# ── Mentorship ────────────────────────────────────────────────────────────────

class OpMentor(Base):
    __tablename__ = "op_mentors"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    email = Column(String(128))
    phone = Column(String(20))
    mentor_type = Column(String(16), default="professional")  # professional, teacher, parent
    state = Column(String(16), default="pending")  # pending, approved, suspended, rejected
    profession = Column(String(128))
    bio = Column(Text)
    active = Column(Boolean, default=True)
    expertise_subjects = relationship("OpSubject", secondary=mentor_subject_rel)
    groups = relationship("OpMentorshipGroup", secondary=mentorship_group_mentor_rel, back_populates="mentors")


class OpMentorshipGroup(Base):
    __tablename__ = "op_mentorship_groups"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    is_open = Column(Boolean, default=True)
    active = Column(Boolean, default=True)
    mentors = relationship("OpMentor", secondary=mentorship_group_mentor_rel, back_populates="groups")
    students = relationship("OpStudent", secondary=mentorship_group_student_rel)
    subjects = relationship("OpSubject", secondary=mentorship_group_subject_rel)
    messages = relationship("OpMentorshipMessage", back_populates="group")


class OpMentorshipMessage(Base):
    __tablename__ = "op_mentorship_messages"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("op_students.id"))
    mentor_id = Column(Integer, ForeignKey("op_mentors.id"))
    group_id = Column(Integer, ForeignKey("op_mentorship_groups.id"))
    subject_id = Column(Integer, ForeignKey("op_subjects.id"))
    message_type = Column(String(16), nullable=False, default="direct_message")  # direct_message, group_question, group_answer
    state = Column(String(16), default="open")  # open, answered, closed
    subject_line = Column(String(256), nullable=False)
    body = Column(Text, nullable=False)
    ai_category_tags = Column(String(256))
    parent_id = Column(Integer, ForeignKey("op_mentorship_messages.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    student = relationship("OpStudent")
    mentor = relationship("OpMentor")
    group = relationship("OpMentorshipGroup", back_populates="messages")
    replies = relationship("OpMentorshipMessage", foreign_keys=[parent_id])
