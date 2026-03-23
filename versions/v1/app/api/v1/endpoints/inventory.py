"""Inventory management endpoints."""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.extras import InventoryCategory, InventoryItem, InventoryTransaction

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str

class ItemCreate(BaseModel):
    name: str
    code: Optional[str] = None
    category_id: Optional[int] = None
    quantity: float = 0
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    reorder_level: Optional[float] = None
    description: Optional[str] = None

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    reorder_level: Optional[float] = None
    description: Optional[str] = None

class TransactionCreate(BaseModel):
    item_id: int
    transaction_type: str   # in | out | adjustment
    quantity: float
    date: date
    reference: Optional[str] = None
    note: Optional[str] = None


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories")
def list_categories(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(InventoryCategory).all()

@router.post("/categories", status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = InventoryCategory(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# ── Items ─────────────────────────────────────────────────────────────────────

@router.get("/items")
def list_items(
    category_id: Optional[int] = None,
    low_stock: bool = False,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(InventoryItem).filter_by(active=True)
    if category_id: q = q.filter_by(category_id=category_id)
    if low_stock:
        q = q.filter(InventoryItem.quantity <= InventoryItem.reorder_level)
    total = q.count()
    items = q.order_by(InventoryItem.name).offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": i.id, "name": i.name, "code": i.code,
         "category": i.category.name if i.category else None,
         "quantity": i.quantity, "unit": i.unit,
         "unit_price": i.unit_price, "reorder_level": i.reorder_level,
         "low_stock": (i.quantity <= i.reorder_level) if i.reorder_level else False}
        for i in items
    ]}

@router.post("/items", status_code=201)
def create_item(data: ItemCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = InventoryItem(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "name": obj.name, "quantity": obj.quantity}

@router.get("/items/{id}")
def get_item(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(InventoryItem).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Item not found")
    return {"id": obj.id, "name": obj.name, "code": obj.code,
            "quantity": obj.quantity, "unit": obj.unit,
            "unit_price": obj.unit_price, "reorder_level": obj.reorder_level,
            "transactions": [
                {"id": t.id, "type": t.transaction_type, "quantity": t.quantity,
                 "date": t.date, "reference": t.reference}
                for t in obj.transactions
            ]}

@router.put("/items/{id}")
def update_item(id: int, data: ItemUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(InventoryItem).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Item not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "name": obj.name, "quantity": obj.quantity}

@router.delete("/items/{id}", status_code=204)
def delete_item(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(InventoryItem).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Item not found")
    obj.active = False; db.commit()


# ── Transactions ──────────────────────────────────────────────────────────────

@router.get("/transactions")
def list_transactions(
    item_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(InventoryTransaction)
    if item_id: q = q.filter_by(item_id=item_id)
    if transaction_type: q = q.filter_by(transaction_type=transaction_type)
    total = q.count()
    items = q.order_by(InventoryTransaction.date.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": t.id, "item_id": t.item_id,
         "item_name": t.item.name if t.item else None,
         "type": t.transaction_type, "quantity": t.quantity,
         "date": t.date, "reference": t.reference, "note": t.note}
        for t in items
    ]}

@router.post("/transactions", status_code=201)
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db),
                       current_user=Depends(get_current_user)):
    item = db.query(InventoryItem).filter_by(id=data.item_id, active=True).first()
    if not item: raise HTTPException(404, "Item not found")

    # Update stock quantity
    if data.transaction_type == "in":
        item.quantity += data.quantity
    elif data.transaction_type == "out":
        if item.quantity < data.quantity:
            raise HTTPException(400, "Insufficient stock")
        item.quantity -= data.quantity
    else:  # adjustment
        item.quantity = data.quantity

    txn = InventoryTransaction(**data.model_dump(), created_by=current_user.id)
    db.add(txn); db.commit(); db.refresh(txn)
    return {"id": txn.id, "item_id": txn.item_id, "type": txn.transaction_type,
            "quantity": txn.quantity, "new_stock": item.quantity}
