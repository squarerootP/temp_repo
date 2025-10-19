from typing import Optional

from sqlalchemy.orm import Session

from backend.src.application.interfaces.borrowing_repository import \
    BorrowingRepository
from backend.src.application.use_cases import book_ops, borrowing_ops
from backend.src.domain.entities.models import BorrowingManager
from backend.src.presentation.schemas import borrowing_schema


def update_borrowing(borrowing_repo: BorrowingRepository, borrow_id: int, borrowing: borrowing_schema.BorrowingUpdate) -> Optional[BorrowingManager]:
    return borrowing_repo.update(borrow_id, borrowing)