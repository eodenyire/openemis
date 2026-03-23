from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.api.crud import get_one, get_all, create_obj, update_obj, delete_obj
from app.models.library import MediaType, Author, Publisher, LibraryTag, Media, MediaMovement
from app.schemas.library import (
    MediaTypeCreate, MediaTypeOut,
    AuthorCreate, AuthorOut,
    PublisherCreate, PublisherOut,
    LibraryTagCreate, LibraryTagOut,
    MediaCreate, MediaUpdate, MediaOut,
    MediaMovementCreate, MediaMovementUpdate, MediaMovementOut,
)

router = APIRouter()

# ── Reference data ────────────────────────────────────────────────────────────
@router.get("/media-types", response_model=List[MediaTypeOut], tags=["Library"])
def list_media_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, MediaType)

@router.post("/media-types", response_model=MediaTypeOut, status_code=201, tags=["Library"])
def create_media_type(data: MediaTypeCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, MediaType, data.model_dump())

@router.get("/authors", response_model=List[AuthorOut], tags=["Library"])
def list_authors(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, Author)

@router.post("/authors", response_model=AuthorOut, status_code=201, tags=["Library"])
def create_author(data: AuthorCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, Author, data.model_dump())

@router.get("/publishers", response_model=List[PublisherOut], tags=["Library"])
def list_publishers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, Publisher)

@router.post("/publishers", response_model=PublisherOut, status_code=201, tags=["Library"])
def create_publisher(data: PublisherCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, Publisher, data.model_dump())

@router.get("/tags", response_model=List[LibraryTagOut], tags=["Library"])
def list_tags(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return get_all(db, LibraryTag)

@router.post("/tags", response_model=LibraryTagOut, status_code=201, tags=["Library"])
def create_tag(data: LibraryTagCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, LibraryTag, data.model_dump())

# ── Media (Books) ─────────────────────────────────────────────────────────────
@router.get("/", response_model=List[MediaOut], tags=["Library"])
def list_media(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               _=Depends(get_current_user)):
    return get_all(db, Media, skip, limit)

@router.post("/", response_model=MediaOut, status_code=201, tags=["Library"])
def create_media(data: MediaCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_obj(db, Media, data.model_dump())

@router.get("/{id}", response_model=MediaOut, tags=["Library"])
def get_media(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, Media, id)
    if not obj:
        raise HTTPException(404, "Media not found")
    return obj

@router.put("/{id}", response_model=MediaOut, tags=["Library"])
def update_media(id: int, data: MediaUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Media, id)
    if not obj:
        raise HTTPException(404, "Media not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/{id}", status_code=204, tags=["Library"])
def delete_media(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = get_one(db, Media, id)
    if not obj:
        raise HTTPException(404, "Media not found")
    delete_obj(db, obj)

# ── Movements (Issue / Return) ────────────────────────────────────────────────
@router.get("/movements/", response_model=List[MediaMovementOut], tags=["Library"])
def list_movements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
    return get_all(db, MediaMovement, skip, limit)

@router.post("/movements/", response_model=MediaMovementOut, status_code=201, tags=["Library"])
def create_movement(data: MediaMovementCreate, db: Session = Depends(get_db),
                    _=Depends(get_current_user)):
    return create_obj(db, MediaMovement, data.model_dump())

@router.get("/movements/{id}", response_model=MediaMovementOut, tags=["Library"])
def get_movement(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, MediaMovement, id)
    if not obj:
        raise HTTPException(404, "Movement not found")
    return obj

@router.put("/movements/{id}", response_model=MediaMovementOut, tags=["Library"])
def update_movement(id: int, data: MediaMovementUpdate, db: Session = Depends(get_db),
                    _=Depends(require_admin)):
    obj = get_one(db, MediaMovement, id)
    if not obj:
        raise HTTPException(404, "Movement not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))
