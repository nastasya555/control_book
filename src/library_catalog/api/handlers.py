import uuid
from typing import Optional
from fastapi import FastAPI, APIRouter, Depends, HTTPException
import uvicorn
from sqlalchemy.orm import Session
from ..database import get_db
from ..repository import BookRepository
from ..external.openlibrary_client import OpenLibraryClient
from .models import BookCreate, ShowBook, DeleteBookResponse, UpdatedBookResponse, UpdatedBookRequest
from typing import List


book_router = APIRouter()

def _create_new_book(body:BookCreate, db):
    # Обогащение данных из Open Library (не влияет на сохранение в БД)
    ol = OpenLibraryClient()
    extra = ol.enrich(title=body.title, author=body.author, isbn=body.isbn)

    book_repository = BookRepository(db)
    book = book_repository.create_book(
        title=body.title,
        author=body.author,
        year=body.year,
        genre=body.genre,
        pages=body.pages,
    )
    return ShowBook(
        book_id=book.book_id,
        title=book.title,
        author=book.author,
        year=book.year,
        genre=book.genre,
        pages=book.pages,
        available=book.available,
        extra=extra or None,
    )


def _delete_book(book_id, db):
    book_repository = BookRepository(db)
    deleted_book_id = book_repository.delete_book(book_id=book_id)
    return deleted_book_id


def _get_book(book_id, db):
    book_repository = BookRepository(db)
    book = book_repository.get_book(book_id=book_id)
    if book is not None:
        return ShowBook(
            book_id=book.book_id,
            title=book.title, 
            author=book.author, 
            year=book.year, 
            genre=book.genre, 
            pages=book.pages,
            available=book.available,
        )


def _update_book(book_id, body, db):
    book_repository = BookRepository(db)
    update_book_id = book_repository.update_book(book_id=book_id, **body.model_dump(exclude_none=True))
    return update_book_id

def _get_books(author_substr: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        available: Optional[bool] = None,
        title_substr: Optional[str] = None,
        db:Session = Depends(get_db)):
    book_repository = BookRepository(db)
    books = book_repository.get_books(author_substr=author_substr, genre=genre, year=year, available=available, title_substr=title_substr)
    return books


@book_router.post("/", response_model=ShowBook)
def create_book(body: BookCreate, db: Session = Depends(get_db)):
    return _create_new_book(body,db)

@book_router.delete("/", response_model=DeleteBookResponse)
def delete_book(book_id: uuid.UUID, db: Session = Depends(get_db)):
    deleted_book_id = _delete_book(book_id, db)
    if deleted_book_id is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return DeleteBookResponse(deleted_book_id=deleted_book_id)

@book_router.get("/{book_id}", response_model=ShowBook)
def get_book(book_id: uuid.UUID, db: Session = Depends(get_db)):
    book = _get_book(book_id=book_id, db=db)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return book

@book_router.patch("/", response_model=UpdatedBookResponse)
def update_book(book_id: uuid.UUID, body: UpdatedBookRequest, db: Session = Depends(get_db)):
    if body.model_dump(exclude_none=True)=={}:
        raise HTTPException(status_code=400, detail=f"At least one parameter for book update should be provided")
    book = _get_book(book_id=book_id, db=db)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    update_book_id = _update_book(book_id=book_id, body=body, db=db)
    return UpdatedBookResponse(update_book_id=update_book_id)

@book_router.get("/", response_model=List[ShowBook])
def get_books(author_substr: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        available: Optional[bool] = None,
        title_substr: Optional[str] = None,
        db:Session = Depends(get_db)):
    books = _get_books(author_substr=author_substr, genre=genre, year=year, available=available, title_substr=title_substr, db=db)
    return books