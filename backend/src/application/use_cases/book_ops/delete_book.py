from backend.src.application.interfaces.book_repository import BookRepository

def delete_book(book_repo: BookRepository, book_id: int) -> None:
    """Business logic for deleting a book."""
    return book_repo.delete(book_id)