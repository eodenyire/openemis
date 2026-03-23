from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class MediaTypeBase(BaseModel):
    name: str
class MediaTypeCreate(MediaTypeBase): pass
class MediaTypeOut(MediaTypeBase):
    id: int
    class Config: from_attributes = True

class AuthorBase(BaseModel):
    name: str
    bio: Optional[str] = None
class AuthorCreate(AuthorBase): pass
class AuthorOut(AuthorBase):
    id: int
    class Config: from_attributes = True

class PublisherBase(BaseModel):
    name: str
class PublisherCreate(PublisherBase): pass
class PublisherOut(PublisherBase):
    id: int
    class Config: from_attributes = True

class LibraryTagBase(BaseModel):
    name: str
class LibraryTagCreate(LibraryTagBase): pass
class LibraryTagOut(LibraryTagBase):
    id: int
    class Config: from_attributes = True


class MediaBase(BaseModel):
    name: str
    isbn: Optional[str] = None
    internal_code: Optional[str] = None
    edition: Optional[str] = None
    description: Optional[str] = None
    media_type_id: Optional[int] = None
    publisher_id: Optional[int] = None
    grade_level: Optional[str] = None
    subject_area: Optional[str] = None
    resource_format: Optional[str] = None
    total_copies: Optional[int] = 1

class MediaCreate(MediaBase): pass
class MediaUpdate(BaseModel):
    name: Optional[str] = None
    total_copies: Optional[int] = None
    available_copies: Optional[int] = None
class MediaOut(MediaBase):
    id: int
    available_copies: int
    class Config: from_attributes = True


class MediaMovementBase(BaseModel):
    media_id: int
    student_id: int
    issue_date: date
    due_date: Optional[date] = None

class MediaMovementCreate(MediaMovementBase): pass
class MediaMovementUpdate(BaseModel):
    return_date: Optional[date] = None
    state: Optional[str] = None
    fine: Optional[int] = None
class MediaMovementOut(MediaMovementBase):
    id: int
    return_date: Optional[date] = None
    state: str
    fine: int
    class Config: from_attributes = True
