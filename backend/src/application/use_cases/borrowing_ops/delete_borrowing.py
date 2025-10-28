from backend.src.application.interfaces.library_interfaces.borrowing_repository import \
    BorrowingRepository
from backend.src.domain.exceptions.borrowing_exceptions import \
    BorrowingNotFoundException


def delete_borrowing(borrowing_repo: BorrowingRepository, borrow_id: int) -> bool:
    if borrowing_repo.get_by_id(borrow_id) is None:
        raise BorrowingNotFoundException.by_id(borrow_id)
    
    return borrowing_repo.delete(borrow_id)