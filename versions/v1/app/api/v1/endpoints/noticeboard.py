"""Notice Board & Blog endpoints."""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.extras import NoticeBoard, BlogCategory, BlogPost, BlogComment

router = APIRouter()


# ── Notice Board ──────────────────────────────────────────────────────────────

class NoticeCreate(BaseModel):
    title: str
    content: str
    target_audience: str = "all"   # all | students | teachers | parents
    expiry_date: Optional[datetime] = None

class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    target_audience: Optional[str] = None
    expiry_date: Optional[datetime] = None
    active: Optional[bool] = None


@router.get("/notices")
def list_notices(
    audience: Optional[str] = None,
    active_only: bool = True,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(NoticeBoard)
    if active_only: q = q.filter_by(active=True)
    if audience: q = q.filter(
        (NoticeBoard.target_audience == audience) | (NoticeBoard.target_audience == "all")
    )
    total = q.count()
    items = q.order_by(NoticeBoard.posted_date.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": n.id, "title": n.title, "content": n.content,
         "target_audience": n.target_audience, "posted_date": n.posted_date,
         "expiry_date": n.expiry_date, "active": n.active}
        for n in items
    ]}

@router.post("/notices", status_code=201)
def create_notice(data: NoticeCreate, db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    obj = NoticeBoard(**data.model_dump(), posted_by=current_user.id)
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "title": obj.title}

@router.get("/notices/{id}")
def get_notice(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(NoticeBoard).filter_by(id=id).first()
    if not obj: raise HTTPException(404, "Notice not found")
    return {"id": obj.id, "title": obj.title, "content": obj.content,
            "target_audience": obj.target_audience, "posted_date": obj.posted_date,
            "expiry_date": obj.expiry_date, "active": obj.active}

@router.put("/notices/{id}")
def update_notice(id: int, data: NoticeUpdate, db: Session = Depends(get_db),
                  _=Depends(get_current_user)):
    obj = db.query(NoticeBoard).filter_by(id=id).first()
    if not obj: raise HTTPException(404, "Notice not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "title": obj.title}

@router.delete("/notices/{id}", status_code=204)
def delete_notice(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(NoticeBoard).filter_by(id=id).first()
    if not obj: raise HTTPException(404, "Notice not found")
    obj.active = False; db.commit()


# ── Blog ──────────────────────────────────────────────────────────────────────

class BlogCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class BlogPostCreate(BaseModel):
    title: str
    content: str
    category_id: Optional[int] = None
    grade_level: Optional[str] = None
    published: bool = False

class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    published: Optional[bool] = None

class CommentCreate(BaseModel):
    content: str


@router.get("/blog/categories")
def list_blog_categories(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(BlogCategory).all()

@router.post("/blog/categories", status_code=201)
def create_blog_category(data: BlogCategoryCreate, db: Session = Depends(get_db),
                          _=Depends(get_current_user)):
    obj = BlogCategory(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/blog/posts")
def list_posts(
    published_only: bool = True,
    category_id: Optional[int] = None,
    skip: int = 0, limit: int = 20,
    db: Session = Depends(get_db), _=Depends(get_current_user)
):
    q = db.query(BlogPost).filter_by(active=True)
    if published_only: q = q.filter_by(published=True)
    if category_id: q = q.filter_by(category_id=category_id)
    total = q.count()
    items = q.order_by(BlogPost.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": p.id, "title": p.title, "category": p.category.name if p.category else None,
         "author_id": p.author_id, "published": p.published,
         "grade_level": p.grade_level, "created_at": p.created_at}
        for p in items
    ]}

@router.post("/blog/posts", status_code=201)
def create_post(data: BlogPostCreate, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    payload = data.model_dump()
    if payload.get("published"):
        payload["published_date"] = datetime.utcnow()
    obj = BlogPost(**payload, author_id=current_user.id)
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "title": obj.title, "published": obj.published}

@router.get("/blog/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(BlogPost).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Post not found")
    return {"id": obj.id, "title": obj.title, "content": obj.content,
            "category": obj.category.name if obj.category else None,
            "author_id": obj.author_id, "published": obj.published,
            "grade_level": obj.grade_level, "created_at": obj.created_at,
            "comments": [{"id": c.id, "content": c.content, "author_id": c.author_id,
                           "approved": c.approved, "created_at": c.created_at}
                          for c in obj.comments if c.approved]}

@router.put("/blog/posts/{id}")
def update_post(id: int, data: BlogPostUpdate, db: Session = Depends(get_db),
                _=Depends(get_current_user)):
    obj = db.query(BlogPost).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Post not found")
    payload = data.model_dump(exclude_none=True)
    if payload.get("published") and not obj.published:
        payload["published_date"] = datetime.utcnow()
    for k, v in payload.items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "title": obj.title, "published": obj.published}

@router.delete("/blog/posts/{id}", status_code=204)
def delete_post(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(BlogPost).filter_by(id=id, active=True).first()
    if not obj: raise HTTPException(404, "Post not found")
    obj.active = False; db.commit()

@router.post("/blog/posts/{id}/comments", status_code=201)
def add_comment(id: int, data: CommentCreate, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    post = db.query(BlogPost).filter_by(id=id, active=True).first()
    if not post: raise HTTPException(404, "Post not found")
    comment = BlogComment(post_id=id, author_id=current_user.id, content=data.content)
    db.add(comment); db.commit(); db.refresh(comment)
    return {"id": comment.id, "approved": comment.approved}

@router.put("/blog/comments/{id}/approve")
def approve_comment(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(BlogComment).filter_by(id=id).first()
    if not obj: raise HTTPException(404, "Comment not found")
    obj.approved = True; db.commit()
    return {"id": obj.id, "approved": True}
