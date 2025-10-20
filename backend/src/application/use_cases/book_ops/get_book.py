from typing import List, Optional

from backend.src.application.interfaces.book_repository import BookRepository
from backend.src.domain.entities.book import Book
from backend.src.domain.exceptions.book_exceptions import BookNotFound


def get_book_by_isbn(book_repo: BookRepository, isbn: str) -> Book:
    """Business logic for getting a book by ISBN."""
    book = book_repo.get_by_isbn(book_isbn=isbn)
    if not book:
        raise BookNotFound.by_isbn(isbn)
    return book

def get_books(book_repo: BookRepository, skip: int = 0, limit: int = 100) -> List[Book]:
    """Business logic for listing books with pagination."""
    return book_repo.list(skip=skip, limit=limit)




