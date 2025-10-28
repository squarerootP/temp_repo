from backend.src.application.interfaces.library_interfaces.borrowing_repository import \
    BorrowingRepository
from backend.src.domain.entities.library_entities.borrowing import \
    BorrowingManager
from backend.src.domain.exceptions.borrowing_exceptions import \
    BorrowingNotYetReturnedException


def create_borrowing(borrowing_repo: BorrowingRepository, data: dict) -> BorrowingManager:
    """Business logic for creating a borrowing record."""
    borrowing = BorrowingManager(**data)
    
    if borrowing_repo.is_currently_borrowed(book_id=borrowing.book_isbn):
        raise BorrowingNotYetReturnedException.for_book(borrowing.book_isbn)
    
    return borrowing_repo.create(borrowing)
