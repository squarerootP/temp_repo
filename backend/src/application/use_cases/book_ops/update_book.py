from typing import Optional

from backend.src.application.interfaces.book_repository import BookRepository
from backend.src.domain.entities.book import Book
from backend.src.domain.exceptions.book_exceptions import BookNotFound


def update_book(book_repo: BookRepository, book_isbn: str, book_data: dict) -> Optional[Book]:
    """Business logic for updating a book."""
    book = book_repo.get_by_isbn(book_isbn=book_isbn)
    if not book:
        raise BookNotFound.by_isbn(book_isbn)
    return book_repo.update(book_isbn, book_data)