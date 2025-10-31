from backend.src.application.interfaces.library_interfaces.book_repository import \
    BookRepository
from backend.src.domain.entities.library_entities.user import User
from backend.src.domain.exceptions.book_exceptions import BookNotFound


class DeleteBookUseCase:
    def __init__(self, book_repo: BookRepository):
        self.book_repo = book_repo

    def execute(self, current_user: User, book_isbn: str) -> bool:
        """Business logic for deleting a book."""
        if current_user.role != "admin":
            raise PermissionError("You do not have permission to delete a book.")
        db_book = self.book_repo.get_by_isbn(book_isbn=book_isbn)
        if not db_book:
            raise BookNotFound.by_isbn(book_isbn)
        return self.book_repo.delete(book_isbn)
