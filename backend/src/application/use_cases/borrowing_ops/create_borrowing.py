from backend.src.application.interfaces.borrowing_repository import \
    BorrowingRepository
from backend.src.domain.entities.borrowing import BorrowingManager


def create_borrowing(borrowing_repo: BorrowingRepository, data: dict) -> BorrowingManager:
    """Business logic for creating a borrowing record."""
    borrowing = BorrowingManager(**data)
    
    if borrowing_repo.is_currently_borrowed(book_id=borrowing.book_isbn):
        raise ValueError("Book is already borrowed and not yet returned.")
    
    return borrowing_repo.create(borrowing)
