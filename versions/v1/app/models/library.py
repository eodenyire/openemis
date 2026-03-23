"""Library module models"""
import enum
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

media_authors = Table("media_authors", Base.metadata,
    Column("media_id", Integer, ForeignKey("media.id", ondelete="CASCADE")),
    Column("author_id", Integer, ForeignKey("authors.id", ondelete="CASCADE")),
)
media_tags = Table("media_tags", Base.metadata,
    Column("media_id", Integer, ForeignKey("media.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("library_tags.id", ondelete="CASCADE")),
)


class MediaMovementState(str, enum.Enum):
    ISSUED = "issued"
    RETURNED = "returned"
    OVERDUE = "overdue"
    LOST = "lost"


class MediaType(Base):
    __tablename__ = "media_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    media = relationship("Media", back_populates="media_type")


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    bio = Column(Text)
    active = Column(Boolean, default=True)


class Publisher(Base):
    __tablename__ = "publishers"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    active = Column(Boolean, default=True)


class LibraryTag(Base):
    __tablename__ = "library_tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)


class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    isbn = Column(String(50), unique=True)
    internal_code = Column(String(50), unique=True)
    edition = Column(String(50))
    description = Column(Text)
    media_type_id = Column(Integer, ForeignKey("media_types.id"))
    publisher_id = Column(Integer, ForeignKey("publishers.id"))
    grade_level = Column(String(20))
    subject_area = Column(String(100))
    resource_format = Column(String(50))   # book, pdf, video, audio…
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    media_type = relationship("MediaType", back_populates="media")
    publisher = relationship("Publisher")
    authors = relationship("Author", secondary=media_authors)
    tags = relationship("LibraryTag", secondary=media_tags)
    movements = relationship("MediaMovement", back_populates="media")


class MediaMovement(Base):
    __tablename__ = "media_movements"
    id = Column(Integer, primary_key=True)
    media_id = Column(Integer, ForeignKey("media.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date)
    return_date = Column(Date)
    state = Column(Enum(MediaMovementState), default=MediaMovementState.ISSUED)
    fine = Column(Integer, default=0)
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    media = relationship("Media", back_populates="movements")
    student = relationship("Student")
