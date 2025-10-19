from sqlalchemy.orm import Session

from backend.src.application.interfaces.borrowing_repository import \
    BorrowingRepository
from backend.src.application.use_cases import borrowing_ops


def delete_borrowing(borrowing_repo: BorrowingRepository, borrow_id: int) -> bool:
    return borrowing_repo.delete(borrow_id)