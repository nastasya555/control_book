from typing import List, Optional
from uuid import UUID

from ...api.v1.schemas.book import (
    BookCreate,
    BookFilters,
    ShowBook,
    UpdatedBookRequest,
)
from ...api.v1.schemas.common import PaginationParams
from ...data.repositories.book_repository import BookRepository
from ...domain.mappers.book_mapper import BookMapper
from ...external.openlibrary.client import OpenLibraryClient


class BookService:
    """Бизнес-логика работы с книгами."""

    def __init__(
        self,
        book_repository: BookRepository,
        openlibrary_client: OpenLibraryClient,
    ):
        self.book_repo = book_repository
        self.ol_client = openlibrary_client

    def create_book(self, book_data: BookCreate) -> ShowBook:
        """Создать книгу с обогащением данных из Open Library."""
        # Бизнес-логика обогащения
        extra = self.ol_client.enrich(
            title=book_data.title,
            author=book_data.author,
            isbn=book_data.isbn,
        )

        # Создание через репозиторий
        book = self.book_repo.create_book(
            title=book_data.title,
            author=book_data.author,
            year=book_data.year,
            genre=book_data.genre,
            pages=book_data.pages,
            extra=extra or None,
        )

        # Маппинг в DTO
        return BookMapper.to_show_book(book)

    def get_book(self, book_id: UUID) -> Optional[ShowBook]:
        """Получить книгу по ID."""
        book = self.book_repo.get_book(book_id)
        if book is None:
            return None
        return BookMapper.to_show_book(book)

    def search_books(
        self, filters: BookFilters, pagination: PaginationParams
    ) -> tuple[List[ShowBook], int]:
        """Поиск книг с фильтрацией и пагинацией."""
        books, total = self.book_repo.search_books(
            author_substr=filters.author_substr,
            genre=filters.genre,
            year=filters.year,
            available=filters.available,
            title_substr=filters.title_substr,
            offset=pagination.offset,
            limit=pagination.page_size,
        )
        return BookMapper.to_show_books(books), total

    def get_books(
        self,
        author_substr: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        available: Optional[bool] = None,
        title_substr: Optional[str] = None,
    ) -> List[ShowBook]:
        """Получить список книг с фильтрацией.

        Без пагинации, для обратной совместимости.
        """
        books = self.book_repo.get_books(
            author_substr=author_substr,
            genre=genre,
            year=year,
            available=available,
            title_substr=title_substr,
        )
        return BookMapper.to_show_books(books)

    def update_book(
        self, book_id: UUID, body: UpdatedBookRequest
    ) -> Optional[UUID]:
        """Обновить книгу. Возвращает book_id или None если не найдена."""
        return self.book_repo.update_book(
            book_id=book_id, **body.model_dump(exclude_none=True)
        )

    def delete_book(self, book_id: UUID) -> Optional[UUID]:
        """Удалить книгу. Возвращает book_id или None если не найдена."""
        return self.book_repo.delete_book(book_id)
