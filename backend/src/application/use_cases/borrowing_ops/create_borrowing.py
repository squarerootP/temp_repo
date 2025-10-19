from backend.src.application.interfaces.borrowing_repository import \
    BorrowingRepository
from backend.src.domain.entities.models import BorrowingManager
from backend.src.presentation.schemas import borrowing_schema


def create_borrowing(borrowing_repo: BorrowingRepository, borrowing: borrowing_schema.BorrowingCreate) -> BorrowingManager:
    return borrowing_repo.create(borrowing)
