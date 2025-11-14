from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from ....api.dependencies import get_book_service
from ....domain.exceptions import BookNotFoundException, DatabaseError
from ....domain.services.book_service import BookService
from ..schemas.book import (
    BookCreate,
    ShowBook,
    DeleteBookResponse,
    UpdatedBookResponse,
    UpdatedBookRequest,
    BookFilters,
)
from ..schemas.common import PaginatedResponse, PaginationParams


book_router = APIRouter()


@book_router.post("/", response_model=ShowBook, status_code=201)
def create_book(
    body: BookCreate,
    service: Annotated[BookService, Depends(get_book_service)],
):
    """Создать новую книгу."""
    try:
        return service.create_book(body)
    except SQLAlchemyError as exc:
        raise DatabaseError() from exc


@book_router.get("/{book_id}", response_model=ShowBook)
def get_book(
    book_id: UUID,
    service: Annotated[BookService, Depends(get_book_service)],
):
    """Получить книгу по ID."""
    try:
        book = service.get_book(book_id)
    except SQLAlchemyError as exc:
        raise DatabaseError() from exc

    if book is None:
        raise BookNotFoundException(book_id)
    return book


@book_router.get("/", response_model=PaginatedResponse[ShowBook])
def get_books(
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[BookFilters, Depends()],
    service: Annotated[BookService, Depends(get_book_service)],
):
    """Получить список книг с фильтрацией и пагинацией."""
    try:
        items, total = service.search_books(filters, pagination)
        return PaginatedResponse.create(items, total, pagination)
    except SQLAlchemyError as exc:
        raise DatabaseError() from exc


@book_router.patch("/{book_id}", response_model=UpdatedBookResponse)
def update_book(
    book_id: UUID,
    body: UpdatedBookRequest,
    service: Annotated[BookService, Depends(get_book_service)],
):
    """Обновить книгу."""
    if body.model_dump(exclude_none=True) == {}:
        raise HTTPException(
            status_code=400,
            detail="At least one parameter for book update should be provided",
        )
    try:
        book = service.get_book(book_id)
    except SQLAlchemyError as exc:
        raise DatabaseError() from exc

    if book is None:
        raise BookNotFoundException(book_id)
    try:
        update_book_id = service.update_book(book_id, body)
    except SQLAlchemyError as exc:
        raise DatabaseError() from exc
    return UpdatedBookResponse(update_book_id=update_book_id)


@book_router.delete("/{book_id}", response_model=DeleteBookResponse)
def delete_book(
    book_id: UUID,
    service: Annotated[BookService, Depends(get_book_service)],
):
    """Удалить книгу."""
    try:
        deleted_book_id = service.delete_book(book_id)
    except SQLAlchemyError as exc:
        raise DatabaseError() from exc

    if deleted_book_id is None:
        raise BookNotFoundException(book_id)
    return DeleteBookResponse(deleted_book_id=deleted_book_id)
