from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Book:
    book_isbn: Optional[int] = None
    isbn: Optional[str] = None
    title: str = ""
    summary: Optional[str] = None
    genre: Optional[str] = None
    published_year: Optional[int] = None
    author_id: Optional[int] = None
    currently_borrowed_by: Optional[int] = None
    # reference to borrowing ids (domain-level)
    borrowing_ids: List[int] = field(default_factory=list)