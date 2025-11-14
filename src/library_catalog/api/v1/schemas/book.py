import uuid
from typing import Optional

from pydantic import BaseModel


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


class BookFilters(BaseModel):
    """Фильтры для поиска книг."""

    author_substr: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    available: Optional[bool] = None
    title_substr: Optional[str] = None
