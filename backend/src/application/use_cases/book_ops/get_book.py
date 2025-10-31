from typing import List, Optional

from backend.src.application.interfaces.library_interfaces.book_repository import \
    BookRepository
from backend.src.domain.entities.library_entities.book import Book
from backend.src.domain.exceptions.book_exceptions import BookNotFound


class GetBookUseCase:
    def __init__(self, book_repo: BookRepository):
        self.book_repo = book_repo

    def get_book_by_isbn(self, isbn: str) -> Book:
        """Business logic for getting a book by ISBN."""
        book = self.book_repo.get_by_isbn(book_isbn=isbn)
        if not book:
            raise BookNotFound.by_isbn(isbn)
        return book

    def get_books(self, skip: int = 0, limit: int = 100) -> List[Book]:
        """Business logic for listing books with pagination."""
        return self.book_repo.list(skip=skip, limit=limit)
