from typing import List, Optional

from sqlalchemy.orm import Session

from backend.src.domain.entities.models import Book
from backend.src.application.interfaces.book_repository import BookRepository

def get_book_by_isbn(book_repo: BookRepository, isbn: str) -> Optional[Book]:
    """Business logic for getting a book by ISBN."""
    return book_repo.get_by_isbn(isbn)

def get_books(book_repo: BookRepository, skip: int = 0, limit: int = 100) -> List[Book]:
    return book_repo.list(skip=skip, limit=limit)




