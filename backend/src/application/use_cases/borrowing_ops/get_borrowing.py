from typing import List, Optional

from sqlalchemy.orm import Session

from backend.src.application.interfaces.borrowing_repository import \
    BorrowingRepository
from backend.src.domain.entities.borrowing import BorrowingManager


def get_borrowing(borrowing_repo: BorrowingRepository, borrow_id: int) -> Optional[BorrowingManager]:
    borrowing = borrowing_repo.get_by_id(borrow_id)
    if not borrowing:
        raise ValueError("Borrowing record not found")
    
    return borrowing

def get_borrowings(
    borrowing_repo: BorrowingRepository, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[BorrowingManager]:
    return borrowing_repo.list(skip, limit, user_id, status)    
