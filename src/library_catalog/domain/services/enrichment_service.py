from typing import Dict, Optional

from ...external.openlibrary.client import OpenLibraryClient


class EnrichmentService:
    """Сервис для обогащения данных книг из внешних источников."""

    def __init__(self, openlibrary_client: OpenLibraryClient):
        self.ol_client = openlibrary_client

    def enrich_book_data(
        self, *, title: str, author: str, isbn: Optional[str] = None
    ) -> Dict:
        """Обогатить данные книги из Open Library."""
        return self.ol_client.enrich(title=title, author=author, isbn=isbn)

