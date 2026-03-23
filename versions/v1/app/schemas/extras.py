from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


# ── Health ────────────────────────────────────────────────────────────────────
class StudentHealthBase(BaseModel):
    student_id: int
    blood_group: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    allergies: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None
    last_checkup_date: Optional[date] = None
    notes: Optional[str] = None
class StudentHealthCreate(StudentHealthBase): pass
class StudentHealthUpdate(BaseModel):
    height: Optional[float] = None
    weight: Optional[float] = None
    allergies: Optional[str] = None
    notes: Optional[str] = None
class StudentHealthOut(StudentHealthBase):
    id: int
    class Config: from_attributes = True

class MedicalConditionBase(BaseModel):
    name: str
    description: Optional[str] = None
class MedicalConditionCreate(MedicalConditionBase): pass
class MedicalConditionOut(MedicalConditionBase):
    id: int
    class Config: from_attributes = True

class VaccinationBase(BaseModel):
    name: str
    description: Optional[str] = None
class VaccinationCreate(VaccinationBase): pass
class VaccinationOut(VaccinationBase):
    id: int
    class Config: from_attributes = True


# ── Achievement ───────────────────────────────────────────────────────────────
class AchievementTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
class AchievementTypeCreate(AchievementTypeBase): pass
class AchievementTypeOut(AchievementTypeBase):
    id: int
    class Config: from_attributes = True

class AchievementBase(BaseModel):
    student_id: int
    achievement_type_id: Optional[int] = None
    title: str
    date: Optional[date] = None
    description: Optional[str] = None
    certificate_number: Optional[str] = None
class AchievementCreate(AchievementBase): pass
class AchievementOut(AchievementBase):
    id: int
    class Config: from_attributes = True


# ── Activity ──────────────────────────────────────────────────────────────────
class ActivityTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
class ActivityTypeCreate(ActivityTypeBase): pass
class ActivityTypeOut(ActivityTypeBase):
    id: int
    class Config: from_attributes = True

class ActivityBase(BaseModel):
    student_id: int
    activity_type_id: Optional[int] = None
    name: str
    date: Optional[date] = None
    description: Optional[str] = None
class ActivityCreate(ActivityBase): pass
class ActivityOut(ActivityBase):
    id: int
    class Config: from_attributes = True


# ── Blog ──────────────────────────────────────────────────────────────────────
class BlogCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
class BlogCategoryCreate(BlogCategoryBase): pass
class BlogCategoryOut(BlogCategoryBase):
    id: int
    class Config: from_attributes = True

class BlogPostBase(BaseModel):
    title: str
    content: str
    category_id: Optional[int] = None
    grade_level: Optional[str] = None
    published: Optional[bool] = False
class BlogPostCreate(BlogPostBase): pass
class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None
class BlogPostOut(BlogPostBase):
    id: int
    author_id: int
    created_at: datetime
    class Config: from_attributes = True

class BlogCommentBase(BaseModel):
    post_id: int
    content: str
class BlogCommentCreate(BlogCommentBase): pass
class BlogCommentOut(BlogCommentBase):
    id: int
    author_id: int
    approved: bool
    created_at: datetime
    class Config: from_attributes = True


# ── Cafeteria ─────────────────────────────────────────────────────────────────
class FoodCategoryBase(BaseModel):
    name: str
class FoodCategoryCreate(FoodCategoryBase): pass
class FoodCategoryOut(FoodCategoryBase):
    id: int
    class Config: from_attributes = True

class MenuItemBase(BaseModel):
    name: str
    category_id: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None
class MenuItemCreate(MenuItemBase): pass
class MenuItemOut(MenuItemBase):
    id: int
    class Config: from_attributes = True

class DailyMenuBase(BaseModel):
    date: date
    description: Optional[str] = None
class DailyMenuCreate(DailyMenuBase): pass
class DailyMenuOut(DailyMenuBase):
    id: int
    class Config: from_attributes = True


# ── Discipline ────────────────────────────────────────────────────────────────
class DisciplineActionBase(BaseModel):
    name: str
    description: Optional[str] = None
class DisciplineActionCreate(DisciplineActionBase): pass
class DisciplineActionOut(DisciplineActionBase):
    id: int
    class Config: from_attributes = True

class DisciplineBase(BaseModel):
    student_id: int
    date: date
    description: str
    action_id: Optional[int] = None
    severity: Optional[str] = "minor"
class DisciplineCreate(DisciplineBase): pass
class DisciplineOut(DisciplineBase):
    id: int
    class Config: from_attributes = True


# ── Event ─────────────────────────────────────────────────────────────────────
class EventTypeBase(BaseModel):
    name: str
class EventTypeCreate(EventTypeBase): pass
class EventTypeOut(EventTypeBase):
    id: int
    class Config: from_attributes = True

class EventBase(BaseModel):
    name: str
    event_type_id: Optional[int] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    max_participants: Optional[int] = None
class EventCreate(EventBase): pass
class EventUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
class EventOut(EventBase):
    id: int
    class Config: from_attributes = True

class EventRegistrationBase(BaseModel):
    event_id: int
    student_id: int
class EventRegistrationCreate(EventRegistrationBase): pass
class EventRegistrationOut(EventRegistrationBase):
    id: int
    status: str
    class Config: from_attributes = True


# ── Facility ──────────────────────────────────────────────────────────────────
class FacilityBase(BaseModel):
    name: str
    facility_type: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    description: Optional[str] = None
class FacilityCreate(FacilityBase): pass
class FacilityOut(FacilityBase):
    id: int
    class Config: from_attributes = True


# ── Inventory ─────────────────────────────────────────────────────────────────
class InventoryCategoryBase(BaseModel):
    name: str
class InventoryCategoryCreate(InventoryCategoryBase): pass
class InventoryCategoryOut(InventoryCategoryBase):
    id: int
    class Config: from_attributes = True

class InventoryItemBase(BaseModel):
    name: str
    code: Optional[str] = None
    category_id: Optional[int] = None
    quantity: Optional[float] = 0
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    reorder_level: Optional[float] = None
    description: Optional[str] = None
class InventoryItemCreate(InventoryItemBase): pass
class InventoryItemUpdate(BaseModel):
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
class InventoryItemOut(InventoryItemBase):
    id: int
    class Config: from_attributes = True

class InventoryTransactionBase(BaseModel):
    item_id: int
    transaction_type: str
    quantity: float
    date: date
    reference: Optional[str] = None
    note: Optional[str] = None
class InventoryTransactionCreate(InventoryTransactionBase): pass
class InventoryTransactionOut(InventoryTransactionBase):
    id: int
    class Config: from_attributes = True


# ── Lesson ────────────────────────────────────────────────────────────────────
class LessonBase(BaseModel):
    name: str
    subject_id: int
    course_id: Optional[int] = None
    faculty_id: Optional[int] = None
    content: Optional[str] = None
    objectives: Optional[str] = None
    duration_minutes: Optional[int] = None
    week_number: Optional[int] = None
class LessonCreate(LessonBase): pass
class LessonUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    objectives: Optional[str] = None
class LessonOut(LessonBase):
    id: int
    class Config: from_attributes = True


# ── LMS ───────────────────────────────────────────────────────────────────────
class LMSContentBase(BaseModel):
    name: str
    content_type: Optional[str] = None
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    duration_minutes: Optional[int] = None
    sequence: Optional[int] = 1
class LMSContentCreate(LMSContentBase): pass
class LMSContentOut(LMSContentBase):
    id: int
    class Config: from_attributes = True

class LMSSectionBase(BaseModel):
    name: str
    sequence: Optional[int] = 1
class LMSSectionCreate(LMSSectionBase):
    contents: Optional[List[LMSContentBase]] = []
class LMSSectionOut(LMSSectionBase):
    id: int
    contents: List[LMSContentOut] = []
    class Config: from_attributes = True

class LMSCourseBase(BaseModel):
    name: str
    description: Optional[str] = None
    course_id: Optional[int] = None
    subject_id: Optional[int] = None
    faculty_id: Optional[int] = None
class LMSCourseCreate(LMSCourseBase): pass
class LMSCourseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
class LMSCourseOut(LMSCourseBase):
    id: int
    class Config: from_attributes = True

class LMSEnrollmentBase(BaseModel):
    lms_course_id: int
    student_id: int
class LMSEnrollmentCreate(LMSEnrollmentBase): pass
class LMSEnrollmentUpdate(BaseModel):
    progress_percent: Optional[float] = None
    completed: Optional[bool] = None
class LMSEnrollmentOut(LMSEnrollmentBase):
    id: int
    progress_percent: float
    completed: bool
    class Config: from_attributes = True


# ── Mentorship ────────────────────────────────────────────────────────────────
class MentorBase(BaseModel):
    first_name: str
    last_name: str
    expertise: Optional[str] = None
    bio: Optional[str] = None
    teacher_id: Optional[int] = None
class MentorCreate(MentorBase): pass
class MentorOut(MentorBase):
    id: int
    approved: bool
    class Config: from_attributes = True

class MentorshipGroupBase(BaseModel):
    name: str
    mentor_id: int
    description: Optional[str] = None
class MentorshipGroupCreate(MentorshipGroupBase): pass
class MentorshipGroupOut(MentorshipGroupBase):
    id: int
    class Config: from_attributes = True

class MentorshipMessageBase(BaseModel):
    group_id: int
    content: str
class MentorshipMessageCreate(MentorshipMessageBase): pass
class MentorshipMessageOut(MentorshipMessageBase):
    id: int
    sender_id: int
    created_at: datetime
    class Config: from_attributes = True


# ── Notice Board ──────────────────────────────────────────────────────────────
class NoticeBoardBase(BaseModel):
    title: str
    content: str
    target_audience: Optional[str] = "all"
    expiry_date: Optional[datetime] = None
class NoticeBoardCreate(NoticeBoardBase): pass
class NoticeBoardUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    expiry_date: Optional[datetime] = None
class NoticeBoardOut(NoticeBoardBase):
    id: int
    posted_by: int
    posted_date: datetime
    class Config: from_attributes = True


# ── Scholarship ───────────────────────────────────────────────────────────────
class ScholarshipTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    amount: Optional[float] = None
class ScholarshipTypeCreate(ScholarshipTypeBase): pass
class ScholarshipTypeOut(ScholarshipTypeBase):
    id: int
    class Config: from_attributes = True

class ScholarshipBase(BaseModel):
    student_id: int
    scholarship_type_id: int
    amount: float
    start_date: date
    end_date: Optional[date] = None
    academic_year_id: Optional[int] = None
    note: Optional[str] = None
class ScholarshipCreate(ScholarshipBase): pass
class ScholarshipUpdate(BaseModel):
    state: Optional[str] = None
    end_date: Optional[date] = None
    note: Optional[str] = None
class ScholarshipOut(ScholarshipBase):
    id: int
    state: str
    class Config: from_attributes = True


# ── DigiGuide ─────────────────────────────────────────────────────────────────
class AcademicPerformanceBase(BaseModel):
    student_id: int
    subject_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    academic_term_id: Optional[int] = None
    assignment_score: Optional[float] = None
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None
    total_score: Optional[float] = None
    grade: Optional[str] = None
class AcademicPerformanceCreate(AcademicPerformanceBase): pass
class AcademicPerformanceOut(AcademicPerformanceBase):
    id: int
    class Config: from_attributes = True

class CareerPathBase(BaseModel):
    name: str
    description: Optional[str] = None
    min_grade: Optional[str] = None
    required_subjects: Optional[str] = None
    university_requirements: Optional[str] = None
class CareerPathCreate(CareerPathBase): pass
class CareerPathOut(CareerPathBase):
    id: int
    class Config: from_attributes = True

class CareerMatchBase(BaseModel):
    student_id: int
    career_id: int
    match_score: Optional[float] = None
    predicted_grade: Optional[str] = None
    recommendation: Optional[str] = None
class CareerMatchCreate(CareerMatchBase): pass
class CareerMatchOut(CareerMatchBase):
    id: int
    class Config: from_attributes = True


# ── Alumni ────────────────────────────────────────────────────────────────────
class AlumniBase(BaseModel):
    student_id: int
    graduation_year: Optional[int] = None
    graduation_date: Optional[date] = None
    final_grade: Optional[str] = None
    current_employer: Optional[str] = None
    current_position: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
class AlumniCreate(AlumniBase): pass
class AlumniUpdate(BaseModel):
    current_employer: Optional[str] = None
    current_position: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
class AlumniOut(AlumniBase):
    id: int
    class Config: from_attributes = True
