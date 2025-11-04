import json
import os
import uuid
from typing import Dict, List, Optional

import portalocker


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_PATH = os.path.normpath(os.path.join(DATA_DIR, "books.json"))


def _ensure_dirs() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def load_all() -> List[Dict]:
    """Загрузить все книги из JSON. Если файла нет — вернуть пустой список."""
    _ensure_dirs()
    if not os.path.exists(DATA_PATH):
        return []
    with portalocker.Lock(DATA_PATH, "r", flags=portalocker.LOCK_SH) as f:
        return json.load(f)


def save_all(books: List[Dict]) -> None:
    """Сохранить список книг атомарно: запись во временный файл и замена."""
    _ensure_dirs()
    tmp_path = f"{DATA_PATH}.tmp"
    # Эксклюзивная блокировка только на время записи временного файла
    with portalocker.Lock(tmp_path, "w", flags=portalocker.LOCK_EX) as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, DATA_PATH)


def create_book(*, title: str, author: str, year: Optional[int] = None,
                genre: Optional[str] = None, pages: Optional[int] = None,
                available: bool = True) -> Dict:
    """Создать книгу и вернуть словарь с полями (book_id — UUID в строке)."""
    books = load_all()
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
    save_all(books)
    return book


def get_book(book_id: str) -> Optional[Dict]:
    books = load_all()
    for b in books:
        if b.get("book_id") == book_id:
            return b
    return None


def list_books(*, author: Optional[str] = None, genre: Optional[str] = None,
               year: Optional[int] = None, available: Optional[bool] = None,
               title_substr: Optional[str] = None,
               limit: int = 50, offset: int = 0) -> List[Dict]:
    books = load_all()

    def matches(b: Dict) -> bool:
        if author is not None and b.get("author") != author:
            return False
        if genre is not None and b.get("genre") != genre:
            return False
        if year is not None and b.get("year") != year:
            return False
        if available is not None and b.get("available") != available:
            return False
        if title_substr:
            title_val = (b.get("title") or "")
            if title_substr.lower() not in title_val.lower():
                return False
        return True

    filtered = [b for b in books if matches(b)]

    if limit is None or limit <= 0:
        limit = 50
    limit = min(limit, 200)
    if offset is None or offset < 0:
        offset = 0

    return filtered[offset : offset + limit]


def update_book(book_id: str, **fields) -> Optional[Dict]:
    """Частичное обновление. Возвращает обновлённую книгу или None."""
    books = load_all()
    updated = None
    for idx, b in enumerate(books):
        if b.get("book_id") == book_id:
            for k, v in fields.items():
                if v is not None:
                    b[k] = v
            books[idx] = b
            updated = b
            break
    if updated is not None:
        save_all(books)
    return updated


def delete_book(book_id: str) -> Optional[str]:
    """Удаление по book_id. Возвращает book_id удалённой книги или None."""
    books = load_all()
    new_books: List[Dict] = []
    deleted: Optional[str] = None
    for b in books:
        if b.get("book_id") == book_id:
            deleted = book_id
        else:
            new_books.append(b)
    if deleted is not None:
        save_all(new_books)
    return deleted


