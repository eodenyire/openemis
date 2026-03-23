"""Cafeteria / Meals endpoints."""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.extras import FoodCategory, MenuItem, DailyMenu

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str

class MenuItemCreate(BaseModel):
    name: str
    category_id: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    active: Optional[bool] = None

class DailyMenuCreate(BaseModel):
    date: date
    description: Optional[str] = None


# ── Food Categories ───────────────────────────────────────────────────────────

@router.get("/categories")
def list_categories(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(FoodCategory).all()

@router.post("/categories", status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = FoodCategory(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# ── Menu Items ────────────────────────────────────────────────────────────────

@router.get("/items")
def list_items(
    category_id: Optional[int] = None,
    active_only: bool = True,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(MenuItem)
    if active_only: q = q.filter_by(active=True)
    if category_id: q = q.filter_by(category_id=category_id)
    items = q.order_by(MenuItem.name).all()
    return [{"id": i.id, "name": i.name, "price": i.price,
             "category": i.category.name if i.category else None,
             "description": i.description, "active": i.active}
            for i in items]

@router.post("/items", status_code=201)
def create_item(data: MenuItemCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = MenuItem(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "name": obj.name, "price": obj.price}

@router.put("/items/{id}")
def update_item(id: int, data: MenuItemUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(MenuItem).filter_by(id=id).first()
    if not obj: raise HTTPException(404, "Item not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "name": obj.name}

@router.delete("/items/{id}", status_code=204)
def delete_item(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(MenuItem).filter_by(id=id).first()
    if not obj: raise HTTPException(404, "Item not found")
    obj.active = False; db.commit()


# ── Daily Menu ────────────────────────────────────────────────────────────────

@router.get("/daily-menu")
def list_daily_menus(
    skip: int = 0, limit: int = 30,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    items = (db.query(DailyMenu).filter_by(active=True)
             .order_by(DailyMenu.date.desc()).offset(skip).limit(limit).all())
    return [{"id": m.id, "date": m.date, "description": m.description} for m in items]

@router.get("/daily-menu/today")
def today_menu(db: Session = Depends(get_db), _=Depends(get_current_user)):
    from datetime import date as dt
    menu = db.query(DailyMenu).filter_by(date=dt.today(), active=True).first()
    if not menu: return {"message": "No menu for today"}
    return {"id": menu.id, "date": menu.date, "description": menu.description}

@router.post("/daily-menu", status_code=201)
def create_daily_menu(data: DailyMenuCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    existing = db.query(DailyMenu).filter_by(date=data.date, active=True).first()
    if existing: raise HTTPException(400, "Menu for this date already exists")
    obj = DailyMenu(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "date": obj.date}

@router.put("/daily-menu/{id}")
def update_daily_menu(id: int, data: DailyMenuCreate, db: Session = Depends(get_db),
                      _=Depends(get_current_user)):
    obj = db.query(DailyMenu).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Menu not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "date": obj.date}
