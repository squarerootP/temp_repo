from datetime import datetime
from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints

from backend.src.presentation.schemas.author_schema import AuthorResponse


class BorrowStatus(str, Enum):
    BORROWED = "borrowed"
    RETURNED = "returned"
    OVERDUE = "overdue"

class BookBase(BaseModel):
    isbn: Annotated[str,
                    StringConstraints(min_length=10, max_length=13)]
    title: str = Field(..., min_length=1, max_length=200)
    summary: Optional[str] = None
    genre: Optional[str] = Field(None, max_length=50)
    published_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    author_id: int

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    summary: Optional[str] = None
    genre: Optional[str] = Field(None, max_length=50)
    published_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    author_id: Optional[int] = None
    currently_borrowed_by: Optional[int] = None

class BookResponse(BookBase):
    book_id: int
    currently_borrowed_by: Optional[int] = None
    
    class ConfigDict:
        from_attributes = True
    
class BookDetailResponse(BookResponse):
    author: AuthorResponse
    
    class ConfigDict:
        from_attributes = True
