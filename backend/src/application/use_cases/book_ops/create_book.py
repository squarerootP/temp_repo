from backend.src.application.interfaces.library_interfaces.book_repository import \
    BookRepository
from backend.src.domain.entities.library_entities.book import Book
from backend.src.domain.entities.library_entities.user import User
from backend.src.domain.exceptions.book_exceptions import BookAlreadyExists


class CreateBookUseCase:
    def __init__(self, book_repo: BookRepository):
        self.book_repo = book_repo

    def execute(self, current_user: User, book: Book) -> Book:
        if current_user.role != "admin":
            raise PermissionError("You do not have permission to create a book.")

        if self.book_repo.get_by_isbn(book.book_isbn):  # type: ignore
            raise BookAlreadyExists.by_isbn(book.book_isbn)  # type: ignore
        return self.book_repo.save(book=book)
