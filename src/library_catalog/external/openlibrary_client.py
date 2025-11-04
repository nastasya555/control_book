import httpx
from typing import Any, Dict, Optional


class OpenLibraryClient:
    """Клиент для Open Library API (https://openlibrary.org/developers/api).

    Использует простой поиск: по ISBN (если задан) или по title+author.
    Возвращает словарь extra с полями: cover_url, description, subjects, pages, year.
    """

    def __init__(self, base_url: str = "https://openlibrary.org", timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _cover_url(self, cover_id: Optional[int]) -> Optional[str]:
        if not cover_id:
            return None
        # https://covers.openlibrary.org/b/id/{cover_id}-L.jpg
        return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

    def search_by_isbn(self, isbn: str) -> Dict[str, Any]:
        # Простой путь: /search.json?isbn=...
        url = f"{self.base_url}/search.json"
        params = {"isbn": isbn, "limit": 1}
        with httpx.Client(timeout=self.timeout) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        docs = data.get("docs", []) or []
        if not docs:
            return {}
        doc = docs[0]
        extra: Dict[str, Any] = {}
        extra["cover_url"] = self._cover_url(doc.get("cover_i"))
        extra["subjects"] = doc.get("subject")
        # Не заполняем pages/year — они приходят от клиента/по умолчанию
        # Описание чаще доступно у works; здесь не тянем, чтобы не усложнять
        extra["description"] = None
        return {k: v for k, v in extra.items() if v is not None}

    def search_by_title_author(self, title: str, author: str) -> Dict[str, Any]:
        url = f"{self.base_url}/search.json"
        params = {"title": title, "author": author, "limit": 1}
        with httpx.Client(timeout=self.timeout) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        docs = data.get("docs", []) or []
        if not docs:
            return {}
        doc = docs[0]
        extra: Dict[str, Any] = {}
        extra["cover_url"] = self._cover_url(doc.get("cover_i"))
        extra["subjects"] = doc.get("subject")
        # Не заполняем pages/year — они приходят от клиента/по умолчанию
        extra["description"] = None
        return {k: v for k, v in extra.items() if v is not None}

    def enrich(self, *, title: str, author: str, isbn: Optional[str] = None) -> Dict[str, Any]:
        if isbn:
            extra = self.search_by_isbn(isbn)
            if extra:
                return extra
        return self.search_by_title_author(title, author)


