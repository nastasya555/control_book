from __future__ import annotations

from uuid import UUID


class DomainException(Exception):
    """Базовое исключение слоя домена."""


class BookNotFoundException(DomainException):
    """Книга не найдена в хранилище."""

    def __init__(self, book_id: UUID) -> None:
        self.book_id = book_id
        super().__init__(f"Book {book_id} not found")


class ExternalServiceError(DomainException):
    """Ошибка при обращении к внешнему сервису."""


class DatabaseError(DomainException):
    """Ошибка взаимодействия с базой данных."""

    def __init__(self, message: str = "Database operation failed") -> None:
        super().__init__(message)

