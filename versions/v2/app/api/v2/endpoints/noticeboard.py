"""Noticeboard and Blog endpoints."""
from typing import Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.models.extras import OpNotice, OpBlogPost

router = APIRouter()


# ── Notices ───────────────────────────────────────────────────────────────────
@router.get("/notices")
def list_notices(notice_type: Optional[str] = None, skip: int = 0, limit: int = 50,
                 db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpNotice).filter_by(active=True)
    if notice_type: q = q.filter_by(notice_type=notice_type)
    q = q.order_by(OpNotice.is_pinned.desc(), OpNotice.published_date.desc())
    return {"total": q.count(), "items": q.offset(skip).limit(limit).all()}

@router.post("/notices", status_code=201)
def create_notice(title: str, body: Optional[str] = None, notice_type: str = "general",
                  published_date: Optional[date] = None, expiry_date: Optional[date] = None,
                  is_pinned: bool = False,
                  db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpNotice(title=title, body=body, notice_type=notice_type,
                   published_date=published_date or date.today(),
                   expiry_date=expiry_date, is_pinned=is_pinned)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/notices/{id}")
def get_notice(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpNotice).get(id)
    if not obj: raise HTTPException(404, "Notice not found")
    return obj

@router.delete("/notices/{id}", status_code=204)
def delete_notice(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpNotice).get(id)
    if not obj: raise HTTPException(404, "Notice not found")
    obj.active = False; db.commit()


# ── Blog Posts ────────────────────────────────────────────────────────────────
@router.get("/blog")
def list_posts(is_published: Optional[bool] = True, skip: int = 0, limit: int = 20,
               db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(OpBlogPost).filter_by(active=True)
    if is_published is not None: q = q.filter_by(is_published=is_published)
    q = q.order_by(OpBlogPost.published_date.desc())
    return {"total": q.count(), "items": q.offset(skip).limit(limit).all()}

@router.post("/blog", status_code=201)
def create_post(title: str, body: Optional[str] = None, author_id: Optional[int] = None,
                is_published: bool = False,
                db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = OpBlogPost(title=title, body=body, author_id=author_id, is_published=is_published,
                     published_date=datetime.utcnow() if is_published else None)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("/blog/{id}")
def get_post(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(OpBlogPost).get(id)
    if not obj: raise HTTPException(404, "Post not found")
    return obj

@router.patch("/blog/{id}/publish")
def publish_post(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = db.query(OpBlogPost).get(id)
    if not obj: raise HTTPException(404, "Post not found")
    obj.is_published = True
    obj.published_date = datetime.utcnow()
    db.commit(); db.refresh(obj); return obj
