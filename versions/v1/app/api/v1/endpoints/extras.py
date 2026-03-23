from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.api.crud import get_one, get_all, create_obj, update_obj, delete_obj
from app.models.health import StudentHealth, MedicalCondition, Vaccination
from app.models.extras import (
    Achievement, AchievementType, Activity, ActivityType,
    BlogPost, BlogCategory, BlogComment,
    MenuItem, FoodCategory, DailyMenu,
    Discipline, DisciplineAction,
    Event, EventType, EventRegistration,
    InventoryItem, InventoryCategory, InventoryTransaction,
    LMSCourse, LMSEnrollment,
    Mentor, MentorshipGroup, MentorshipMessage,
    NoticeBoard, Scholarship, ScholarshipType,
    CareerPath, AcademicPerformance, StudentCareerMatch,
    Alumni,
)
from app.schemas.extras import (
    StudentHealthCreate, StudentHealthUpdate, StudentHealthOut,
    MedicalConditionCreate, MedicalConditionOut,
    VaccinationCreate, VaccinationOut,
    AchievementCreate, AchievementOut, AchievementTypeCreate, AchievementTypeOut,
    ActivityCreate, ActivityOut, ActivityTypeCreate, ActivityTypeOut,
    BlogPostCreate, BlogPostUpdate, BlogPostOut, BlogCategoryCreate, BlogCategoryOut,
    BlogCommentCreate, BlogCommentOut,
    MenuItemCreate, MenuItemOut, FoodCategoryCreate, FoodCategoryOut,
    DailyMenuCreate, DailyMenuOut,
    DisciplineCreate, DisciplineOut, DisciplineActionCreate, DisciplineActionOut,
    EventCreate, EventUpdate, EventOut, EventTypeCreate, EventTypeOut,
    EventRegistrationCreate, EventRegistrationOut,
    InventoryItemCreate, InventoryItemUpdate, InventoryItemOut,
    InventoryCategoryCreate, InventoryCategoryOut,
    InventoryTransactionCreate, InventoryTransactionOut,
    LMSCourseCreate, LMSCourseUpdate, LMSCourseOut,
    LMSEnrollmentCreate, LMSEnrollmentUpdate, LMSEnrollmentOut,
    MentorCreate, MentorOut, MentorshipGroupCreate, MentorshipGroupOut,
    MentorshipMessageCreate, MentorshipMessageOut,
    NoticeBoardCreate, NoticeBoardUpdate, NoticeBoardOut,
    ScholarshipCreate, ScholarshipUpdate, ScholarshipOut,
    ScholarshipTypeCreate, ScholarshipTypeOut,
    CareerPathCreate, CareerPathOut,
    AcademicPerformanceCreate, AcademicPerformanceOut,
    CareerMatchCreate, CareerMatchOut,
    AlumniCreate, AlumniUpdate, AlumniOut,
)

router = APIRouter()


# ── Health ────────────────────────────────────────────────────────────────────
@router.get("/health/", response_model=List[StudentHealthOut], tags=["Health"])
def list_health(skip: int = 0, limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, StudentHealth, skip, limit)

@router.post("/health/", response_model=StudentHealthOut, status_code=201, tags=["Health"])
def create_health(data: StudentHealthCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return create_obj(db, StudentHealth, data.model_dump())

@router.get("/health/{id}", response_model=StudentHealthOut, tags=["Health"])
def get_health(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, StudentHealth, id)
    if not obj: raise HTTPException(404, "Record not found")
    return obj

@router.put("/health/{id}", response_model=StudentHealthOut, tags=["Health"])
def update_health(id: int, data: StudentHealthUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, StudentHealth, id)
    if not obj: raise HTTPException(404, "Record not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/health/{id}", status_code=204, tags=["Health"])
def delete_health(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, StudentHealth, id)
    if not obj: raise HTTPException(404, "Record not found")
    delete_obj(db, obj)

@router.get("/medical-conditions/", response_model=List[MedicalConditionOut], tags=["Health"])
def list_conditions(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, MedicalCondition)

@router.post("/medical-conditions/", response_model=MedicalConditionOut, status_code=201, tags=["Health"])
def create_condition(data: MedicalConditionCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, MedicalCondition, data.model_dump())

@router.get("/vaccinations/", response_model=List[VaccinationOut], tags=["Health"])
def list_vaccinations(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, Vaccination)

@router.post("/vaccinations/", response_model=VaccinationOut, status_code=201, tags=["Health"])
def create_vaccination(data: VaccinationCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, Vaccination, data.model_dump())

# ── Achievements ──────────────────────────────────────────────────────────────
@router.get("/achievement-types/", response_model=List[AchievementTypeOut], tags=["Achievements"])
def list_achievement_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, AchievementType)

@router.post("/achievement-types/", response_model=AchievementTypeOut, status_code=201, tags=["Achievements"])
def create_achievement_type(data: AchievementTypeCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, AchievementType, data.model_dump())

@router.get("/achievements/", response_model=List[AchievementOut], tags=["Achievements"])
def list_achievements(skip: int = 0, limit: int = 200, student_id: int = None,
                      db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(Achievement)
    if student_id: q = q.filter(Achievement.student_id == student_id)
    return q.offset(skip).limit(limit).all()

@router.post("/achievements/", response_model=AchievementOut, status_code=201, tags=["Achievements"])
def create_achievement(data: AchievementCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return create_obj(db, Achievement, data.model_dump())

@router.delete("/achievements/{id}", status_code=204, tags=["Achievements"])
def delete_achievement(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Achievement, id)
    if not obj: raise HTTPException(404, "Achievement not found")
    delete_obj(db, obj)

# ── Blog ──────────────────────────────────────────────────────────────────────
@router.get("/blog/categories/", response_model=List[BlogCategoryOut], tags=["Blog"])
def list_blog_categories(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, BlogCategory)

@router.post("/blog/categories/", response_model=BlogCategoryOut, status_code=201, tags=["Blog"])
def create_blog_category(data: BlogCategoryCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, BlogCategory, data.model_dump())

@router.get("/blog/posts/", response_model=List[BlogPostOut], tags=["Blog"])
def list_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, BlogPost, skip, limit)

@router.post("/blog/posts/", response_model=BlogPostOut, status_code=201, tags=["Blog"])
def create_post(data: BlogPostCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    payload = data.model_dump()
    payload["author_id"] = current_user.id
    return create_obj(db, BlogPost, payload)

@router.put("/blog/posts/{id}", response_model=BlogPostOut, tags=["Blog"])
def update_post(id: int, data: BlogPostUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, BlogPost, id)
    if not obj: raise HTTPException(404, "Post not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/blog/posts/{id}", status_code=204, tags=["Blog"])
def delete_post(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, BlogPost, id)
    if not obj: raise HTTPException(404, "Post not found")
    delete_obj(db, obj)

@router.post("/blog/posts/{post_id}/comments", response_model=BlogCommentOut, status_code=201, tags=["Blog"])
def add_comment(post_id: int, data: BlogCommentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    payload = data.model_dump()
    payload["post_id"] = post_id
    payload["author_id"] = current_user.id
    return create_obj(db, BlogComment, payload)

# ── Cafeteria ─────────────────────────────────────────────────────────────────
@router.get("/cafeteria/categories/", response_model=List[FoodCategoryOut], tags=["Cafeteria"])
def list_food_categories(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, FoodCategory)

@router.post("/cafeteria/categories/", response_model=FoodCategoryOut, status_code=201, tags=["Cafeteria"])
def create_food_category(data: FoodCategoryCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, FoodCategory, data.model_dump())

@router.get("/cafeteria/items/", response_model=List[MenuItemOut], tags=["Cafeteria"])
def list_menu_items(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, MenuItem)

@router.post("/cafeteria/items/", response_model=MenuItemOut, status_code=201, tags=["Cafeteria"])
def create_menu_item(data: MenuItemCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, MenuItem, data.model_dump())

@router.put("/cafeteria/items/{id}", response_model=MenuItemOut, tags=["Cafeteria"])
def update_menu_item(id: int, data: MenuItemCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, MenuItem, id)
    if not obj: raise HTTPException(404, "Item not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/cafeteria/items/{id}", status_code=204, tags=["Cafeteria"])
def delete_menu_item(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, MenuItem, id)
    if not obj: raise HTTPException(404, "Item not found")
    delete_obj(db, obj)

@router.get("/cafeteria/daily-menu/", response_model=List[DailyMenuOut], tags=["Cafeteria"])
def list_daily_menu(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, DailyMenu)

@router.post("/cafeteria/daily-menu/", response_model=DailyMenuOut, status_code=201, tags=["Cafeteria"])
def create_daily_menu(data: DailyMenuCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, DailyMenu, data.model_dump())

# ── Discipline ────────────────────────────────────────────────────────────────
@router.get("/discipline/actions/", response_model=List[DisciplineActionOut], tags=["Discipline"])
def list_discipline_actions(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, DisciplineAction)

@router.post("/discipline/actions/", response_model=DisciplineActionOut, status_code=201, tags=["Discipline"])
def create_discipline_action(data: DisciplineActionCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, DisciplineAction, data.model_dump())

@router.get("/discipline/", response_model=List[DisciplineOut], tags=["Discipline"])
def list_discipline(skip: int = 0, limit: int = 200, student_id: int = None,
                    db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(Discipline)
    if student_id: q = q.filter(Discipline.student_id == student_id)
    return q.offset(skip).limit(limit).all()

@router.post("/discipline/", response_model=DisciplineOut, status_code=201, tags=["Discipline"])
def create_discipline(data: DisciplineCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return create_obj(db, Discipline, data.model_dump())

@router.delete("/discipline/{id}", status_code=204, tags=["Discipline"])
def delete_discipline(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Discipline, id)
    if not obj: raise HTTPException(404, "Record not found")
    delete_obj(db, obj)

# ── Events ────────────────────────────────────────────────────────────────────
@router.get("/events/types/", response_model=List[EventTypeOut], tags=["Events"])
def list_event_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, EventType)

@router.post("/events/types/", response_model=EventTypeOut, status_code=201, tags=["Events"])
def create_event_type(data: EventTypeCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, EventType, data.model_dump())

@router.get("/events/", response_model=List[EventOut], tags=["Events"])
def list_events(skip: int = 0, limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, Event, skip, limit)

@router.post("/events/", response_model=EventOut, status_code=201, tags=["Events"])
def create_event(data: EventCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return create_obj(db, Event, data.model_dump())

@router.put("/events/{id}", response_model=EventOut, tags=["Events"])
def update_event(id: int, data: EventUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, Event, id)
    if not obj: raise HTTPException(404, "Event not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/events/{id}", status_code=204, tags=["Events"])
def delete_event(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Event, id)
    if not obj: raise HTTPException(404, "Event not found")
    delete_obj(db, obj)

@router.post("/events/{event_id}/register", response_model=EventRegistrationOut, status_code=201, tags=["Events"])
def register_for_event(event_id: int, data: EventRegistrationCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    payload = data.model_dump()
    payload["event_id"] = event_id
    return create_obj(db, EventRegistration, payload)

# ── Inventory ─────────────────────────────────────────────────────────────────
@router.get("/inventory/categories/", response_model=List[InventoryCategoryOut], tags=["Inventory"])
def list_inv_categories(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, InventoryCategory)

@router.post("/inventory/categories/", response_model=InventoryCategoryOut, status_code=201, tags=["Inventory"])
def create_inv_category(data: InventoryCategoryCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, InventoryCategory, data.model_dump())

@router.get("/inventory/", response_model=List[InventoryItemOut], tags=["Inventory"])
def list_inventory(skip: int = 0, limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, InventoryItem, skip, limit)

@router.post("/inventory/", response_model=InventoryItemOut, status_code=201, tags=["Inventory"])
def create_inventory_item(data: InventoryItemCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, InventoryItem, data.model_dump())

@router.put("/inventory/{id}", response_model=InventoryItemOut, tags=["Inventory"])
def update_inventory_item(id: int, data: InventoryItemUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, InventoryItem, id)
    if not obj: raise HTTPException(404, "Item not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/inventory/{id}", status_code=204, tags=["Inventory"])
def delete_inventory_item(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, InventoryItem, id)
    if not obj: raise HTTPException(404, "Item not found")
    delete_obj(db, obj)

@router.post("/inventory/transactions/", response_model=InventoryTransactionOut, status_code=201, tags=["Inventory"])
def create_inv_transaction(data: InventoryTransactionCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    item = get_one(db, InventoryItem, data.item_id)
    if not item: raise HTTPException(404, "Item not found")
    tx = create_obj(db, InventoryTransaction, data.model_dump())
    delta = data.quantity if data.transaction_type == "in" else -data.quantity
    update_obj(db, item, {"quantity": (item.quantity or 0) + delta})
    return tx
