from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Book:
    book_isbn: Optional[str] = None
    title: str = ""
    summary: Optional[str] = None
    genre: Optional[str] = None
    published_year: Optional[int] = None
    author_name: Optional[str] = None
    img_path: Optional[str] = None
