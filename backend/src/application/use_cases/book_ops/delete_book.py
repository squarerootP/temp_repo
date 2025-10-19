from backend.src.application.interfaces.book_repository import BookRepository


def delete_book(book_repo: BookRepository, book_isbn: str) -> None:
    """Business logic for deleting a book."""
    book = book_repo.get_by_isbn(book_isbn=book_isbn)
    if not book:
        raise ValueError("Book not found.")
    return book_repo.delete(book_isbn)