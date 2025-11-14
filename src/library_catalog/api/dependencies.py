from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.config import settings
from ..data.repositories.book_repository import BookRepository
from ..external.openlibrary.client import OpenLibraryClient


@lru_cache
def get_openlibrary_client() -> OpenLibraryClient:
    """Singleton для Open Library клиента."""
    return OpenLibraryClient(
        base_url=settings.openlibrary_base_url,
        timeout=settings.openlibrary_timeout,
    )


def get_book_repository(
    db: Annotated[Session, Depends(get_db)]
) -> BookRepository:
    """Создать репозиторий для текущей сессии."""
    return BookRepository(db)


def get_book_service(
    repository: Annotated[BookRepository, Depends(get_book_repository)],
    ol_client: Annotated[OpenLibraryClient, Depends(get_openlibrary_client)],
):
    """Создать сервис с внедренными зависимостями."""
    from ..domain.services.book_service import BookService
    return BookService(repository, ol_client)
