class BorrowingNotFoundException(Exception):
    """Exception raised when a borrowing record is not found."""
    @classmethod
    def by_id(cls, borrow_id: int):
        return cls(f"Borrowing record with id {borrow_id} not found.")

class BorrowingNotYetReturnedException(Exception):
    """Exception raised when trying to delete a borrowing record that has not been returned yet."""
    @classmethod
    def by_id(cls, borrow_id: int):
        return cls(f"Borrowing record with id {borrow_id} has not been returned yet and cannot be deleted.")
    @classmethod
    def for_book(cls, book_isbn: str):
        return cls(f"Book with ISBN {book_isbn} is currently borrowed and not yet returned.")