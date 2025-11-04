import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class TunedMode(BaseModel):
    model_config = {"from_attributes": True}


class BookCreate(BaseModel):
    title: str 
    author: str 
    year: int 
    genre: str 
    pages: int
    isbn: Optional[str] = None  # для обогащения из Open Library


class ShowBook(TunedMode):
    book_id: uuid.UUID
    title: str 
    author: str 
    year: int 
    genre: str 
    pages: int
    available: bool
    extra: Optional[dict] = None  # обложка/описание/subjects и т.д.


class DeleteBookResponse(BaseModel):
    deleted_book_id: uuid.UUID


class UpdatedBookResponse(BaseModel):
    update_book_id: uuid.UUID


class UpdatedBookRequest(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    pages: Optional[int] = None
    available: Optional[bool] = None