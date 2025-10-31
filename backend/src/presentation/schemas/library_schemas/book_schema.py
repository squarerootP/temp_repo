from datetime import datetime
from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints


class BookBase(BaseModel):
    book_isbn: Annotated[str, StringConstraints(min_length=10, max_length=13)]
    title: str = Field(..., min_length=1, max_length=200)
    summary: Optional[str] = None
    genre: Optional[str] = Field(None, max_length=50)
    published_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    author_name: str


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    summary: Optional[str] = None
    genre: Optional[str] = Field(None, max_length=50)
    published_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    author_name: Optional[str] = None


class BookResponse(BookBase):
    book_isbn: str

    class ConfigDict:
        from_attributes = True


class BookDetailResponse(BookResponse):
    pass
