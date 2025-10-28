from backend.src.application.interfaces.library_interfaces.book_repository import \
    BookRepository
from backend.src.domain.exceptions.book_exceptions import BookNotFound


def delete_book(book_repo: BookRepository, book_isbn: str) -> bool:
    """Business logic for deleting a book."""
    book = book_repo.get_by_isbn(book_isbn=book_isbn)
    if not book:
        raise BookNotFound.by_isbn(book_isbn)
    return book_repo.delete(book_isbn)