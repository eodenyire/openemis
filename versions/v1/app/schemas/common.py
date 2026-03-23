"""Shared schema utilities"""
from pydantic import BaseModel
from typing import Optional, List, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: List[T]


class MessageResponse(BaseModel):
    message: str


class IDResponse(BaseModel):
    id: int
