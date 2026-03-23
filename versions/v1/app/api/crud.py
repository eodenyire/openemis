"""Generic CRUD helpers used by all endpoint modules."""
from typing import Type, TypeVar, Optional, List, Any
from sqlalchemy.orm import Session
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


def get_one(db: Session, model: Type[ModelType], id: int) -> Optional[ModelType]:
    return db.query(model).filter(model.id == id).first()


def get_all(db: Session, model: Type[ModelType], skip: int = 0, limit: int = 100,
            filters: Optional[List[Any]] = None) -> List[ModelType]:
    q = db.query(model)
    if filters:
        for f in filters:
            q = q.filter(f)
    return q.offset(skip).limit(limit).all()


def create_obj(db: Session, model: Type[ModelType], data: dict) -> ModelType:
    obj = model(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_obj(db: Session, obj: ModelType, data: dict) -> ModelType:
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_obj(db: Session, obj: ModelType) -> None:
    db.delete(obj)
    db.commit()
