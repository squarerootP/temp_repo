from backend.src.application.interfaces.book_repository import BookRepository
from backend.src.domain.entities.book import Book
from backend.src.domain.exceptions.book_exceptions import BookAlreadyExists


def create_book(book_repo: BookRepository, book_data) -> Book:
    """Business logic for creating a book."""
    book_dict = book_data.model_dump()
    if book_repo.get_by_isbn(book_dict["book_isbn"]):
        raise BookAlreadyExists.by_isbn(book_dict["book_isbn"])
    book = Book(**book_dict)
    book_repo.save(book)
    return book