"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.library_catalog.core.database import Base
from src.library_catalog.data.models.book import Book


@pytest.fixture
def db_session():
    """Создает тестовую сессию БД."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def sample_book(db_session):
    """Создает тестовую книгу."""
    book = Book(
        title="Test Book",
        author="Test Author",
        year=2024,
        genre="Test Genre",
        pages=100,
        available=True,
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    return book

