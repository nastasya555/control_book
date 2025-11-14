from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List

from ...api.v1.schemas.book import ShowBook

if TYPE_CHECKING:  # pragma: no cover
    from ...data.models.book import Book


class BookMapper:
    """Маппер для преобразования сущностей Book в DTO."""

    @staticmethod
    def to_show_book(book: "Book") -> ShowBook:
        return ShowBook(
            book_id=book.book_id,
            title=book.title,
            author=book.author,
            year=book.year,
            genre=book.genre,
            pages=book.pages,
            available=book.available,
            extra=book.extra,
        )

    @staticmethod
    def to_show_books(books: Iterable["Book"]) -> List[ShowBook]:
        return [BookMapper.to_show_book(book) for book in books]
