from typing import Optional

from backend.src.application.interfaces.borrowing_repository import \
    BorrowingRepository
from backend.src.domain.entities.borrowing import BorrowingManager
from backend.src.domain.exceptions.borrowing_exceptions import \
    BorrowingNotFoundException


def update_borrowing(borrowing_repo: BorrowingRepository, borrow_id: int, data: dict) -> Optional[BorrowingManager]:
    borrowing = borrowing_repo.get_by_id(borrow_id=borrow_id)
    if not borrowing:
        raise BorrowingNotFoundException.by_id(borrow_id)
    borrowing = data
    return borrowing_repo.update(borrow_id, borrowing)