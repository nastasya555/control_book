"""Domain модель Book - бизнес-сущность без зависимостей от БД."""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class Book:
    """Доменная модель книги."""

    book_id: UUID
    title: str
    author: str
    year: int
    genre: str
    pages: int
    available: bool
    extra: Optional[dict] = None

