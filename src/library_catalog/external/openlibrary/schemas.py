from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class OpenLibraryDoc(BaseModel):
    """Схема документа из Open Library API."""

    cover_i: Optional[int] = None
    subject: Optional[List[str]] = None
    title: Optional[str] = None
    author_name: Optional[List[str]] = None


class OpenLibrarySearchResponse(BaseModel):
    """Схема ответа поиска Open Library."""

    docs: List[Dict[str, Any]] = []

