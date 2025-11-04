import uuid
from typing import Any, Dict, List, Optional

from .external.jsonbin_client import JsonBinClient


class JsonBinBookRepository:
    """Репозиторий книг поверх jsonbin.io.

    Хранит структуру вида: {"books": [ {...}, ... ]}
    book_id хранится как строка UUID.
    Все операции реализованы по схеме read-modify-write c If-Match.
    """

    def __init__(self, client: JsonBinClient) -> None:
        self.client = client

    def _load(self) -> tuple[Dict[str, Any], str | None]:
        return self.client.read_all()

    def _save(self, record: Dict[str, Any], etag: str | None) -> str:
        return self.client.write_all(record, etag)

    def create_book(
        self,
        *,
        title: str,
        author: str,
        year: Optional[int] = None,
        genre: Optional[str] = None,
        pages: Optional[int] = None,
        available: bool = True,
    ) -> Dict[str, Any]:
        record, etag = self._load()
        books: List[Dict[str, Any]] = list(record.get("books", []))
        book = {
            "book_id": str(uuid.uuid4()),
            "title": title,
            "author": author,
            "year": year,
            "genre": genre,
            "pages": pages,
            "available": available,
        }
        books.append(book)
        new_etag = self._save({"books": books}, etag)
        return book

    def get_book(self, book_id: str) -> Optional[Dict[str, Any]]:
        record, _ = self._load()
        for b in record.get("books", []):
            if b.get("book_id") == book_id:
                return b
        return None

    def list_books(
        self,
        *,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        available: Optional[bool] = None,
        title_substr: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        record, _ = self._load()
        books: List[Dict[str, Any]] = list(record.get("books", []))

        def matches(b: Dict[str, Any]) -> bool:
            if author is not None and b.get("author") != author:
                return False
            if genre is not None and b.get("genre") != genre:
                return False
            if year is not None and b.get("year") != year:
                return False
            if available is not None and b.get("available") != available:
                return False
            if title_substr:
                val = (b.get("title") or "")
                if title_substr.lower() not in val.lower():
                    return False
            return True

        filtered = [b for b in books if matches(b)]
        limit = max(1, min(limit, 200))
        offset = max(0, offset)
        return filtered[offset : offset + limit]

    def update_book(self, book_id: str, **fields) -> Optional[str]:
        record, etag = self._load()
        books: List[Dict[str, Any]] = list(record.get("books", []))
        updated = None
        for idx, b in enumerate(books):
            if b.get("book_id") == book_id:
                for k, v in fields.items():
                    if v is not None:
                        b[k] = v
                books[idx] = b
                updated = book_id
                break
        if updated is None:
            return None
        self._save({"books": books}, etag)
        return updated

    def delete_book(self, book_id: str) -> Optional[str]:
        record, etag = self._load()
        books: List[Dict[str, Any]] = list(record.get("books", []))
        new_books: List[Dict[str, Any]] = []
        deleted = None
        for b in books:
            if b.get("book_id") == book_id:
                deleted = book_id
            else:
                new_books.append(b)
        if deleted is None:
            return None
        self._save({"books": new_books}, etag)
        return deleted


