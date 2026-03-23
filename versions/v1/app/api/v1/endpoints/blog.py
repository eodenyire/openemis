"""Blog module endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.extras import BlogCategory, BlogPost, BlogComment

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class PostCreate(BaseModel):
    title: str
    content: str
    category_id: Optional[int] = None
    published: bool = False
    grade_level: Optional[str] = None
    image: Optional[str] = None

class CommentCreate(BaseModel):
    content: str


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories")
def list_categories(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(BlogCategory).all()

@router.post("/categories", status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db),
                    _=Depends(get_current_user)):
    obj = BlogCategory(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# ── Posts ─────────────────────────────────────────────────────────────────────

@router.get("/")
def list_posts(published_only: bool = True, category_id: Optional[int] = None,
               skip: int = 0, limit: int = 20,
               db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(BlogPost).filter_by(active=True)
    if published_only:
        q = q.filter_by(published=True)
    if category_id:
        q = q.filter_by(category_id=category_id)
    return q.order_by(BlogPost.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/", status_code=201)
def create_post(data: PostCreate, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    from datetime import datetime
    payload = data.model_dump()
    if payload.get("published"):
        payload["published_date"] = datetime.utcnow()
    obj = BlogPost(**payload, author_id=current_user.id)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/{id}")
def get_post(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(BlogPost).get(id)
    if not obj: raise HTTPException(404, "Post not found")
    return obj

@router.put("/{id}")
def update_post(id: int, data: PostCreate, db: Session = Depends(get_db),
                _=Depends(get_current_user)):
    obj = db.query(BlogPost).get(id)
    if not obj: raise HTTPException(404, "Post not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.put("/{id}/publish")
def publish_post(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    from datetime import datetime
    obj = db.query(BlogPost).get(id)
    if not obj: raise HTTPException(404, "Post not found")
    obj.published = True
    obj.published_date = datetime.utcnow()
    db.commit()
    return {"id": obj.id, "published": True}

@router.delete("/{id}")
def delete_post(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(BlogPost).get(id)
    if not obj: raise HTTPException(404, "Post not found")
    obj.active = False
    db.commit()
    return {"status": "deleted"}


# ── Comments ──────────────────────────────────────────────────────────────────

@router.get("/{id}/comments")
def list_comments(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(BlogComment).filter_by(post_id=id, approved=True).all()

@router.post("/{id}/comments", status_code=201)
def add_comment(id: int, data: CommentCreate, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    post = db.query(BlogPost).get(id)
    if not post: raise HTTPException(404, "Post not found")
    obj = BlogComment(post_id=id, author_id=current_user.id, content=data.content)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/comments/{id}/approve")
def approve_comment(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(BlogComment).get(id)
    if not obj: raise HTTPException(404, "Comment not found")
    obj.approved = True
    db.commit()
    return {"id": obj.id, "approved": True}
