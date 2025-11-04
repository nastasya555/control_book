import uuid
from enum import Enum

from pydantic import BaseModel, EmailStr
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase



class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"
    book_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    year = Column(Integer)
    genre = Column(String)
    pages = Column(Integer)
    available = Column(Boolean, default=True, nullable=False)