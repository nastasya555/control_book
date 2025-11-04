from typing import Iterable, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, update
from .models import Book


class BookRepository:
    def __init__(self, db: Session):
        self.db=db

    def create_book(self, title: str, author: str, year: int, genre: str, pages: int):
        new_book=Book(
            title=title,
            author=author,
            year=year,
            genre=genre,
            pages=pages
        )
        self.db.add(new_book)
        self.db.commit()
        self.db.refresh(new_book)
        return new_book

    def delete_book(self, book_id: UUID):
        query = delete(Book).where(Book.book_id == book_id).returning(Book.book_id)
        result = self.db.execute(query)
        deleted_row = result.fetchone()
        if deleted_row is None:
            return None
        self.db.commit()
        return deleted_row[0]
    
    def get_book(self, book_id: UUID):
        query = select(Book).where(Book.book_id == book_id)
        res = self.db.execute(query)
        book_row = res.fetchone()
        if book_row is not None:
            return book_row[0]
    
    def update_book(self, book_id: UUID, **kwargs):
        query = update(Book).where(Book.book_id == book_id).values(**kwargs).returning(Book.book_id)
        res = self.db.execute(query)
        update_row = res.fetchone()
        if update_row is None:
            return None
        self.db.commit()
        return update_row[0]
    
    def get_books(self, 
        author_substr: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        available: Optional[bool] = None,
        title_substr: Optional[str] = None,):
        query = select(Book)
        if author_substr is not None: 
            query = query.where(Book.author.ilike(f"%{author_substr}%"))
        if genre:
            query = query.where(Book.genre == genre)
        if year:
            query = query.where(Book.year == year)
        if available:
            query = query.where(Book.available == available)
        if title_substr is not None: 
            query = query.where(Book.title.ilike(f"%{title_substr}%"))
        
        return list(self.db.execute(query).scalars())