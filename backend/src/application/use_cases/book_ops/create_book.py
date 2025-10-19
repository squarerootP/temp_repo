from backend.src.application.interfaces.book_repository import BookRepository
from backend.src.domain.entities.models import Book


def create_book(book_repo: BookRepository, book_data) -> Book:
    """Business logic for creating a book."""
    book_dict = book_data.model_dump()
    book = Book(**book_dict)
    book_repo.save(book)
    return book