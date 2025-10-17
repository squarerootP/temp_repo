from typing import List, Optional
from backend.src.domain.entities.models import BorrowingManager
from backend.src.presentation.schemas import borrowing_schema

class BorrowingRepository:
    def create(self, borrowing: borrowing_schema.BorrowingCreate) -> BorrowingManager:
        raise NotImplementedError

    def get_by_id(self, borrow_id: int) -> Optional[BorrowingManager]:
        raise NotImplementedError

    def list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        user_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[BorrowingManager]:
        raise NotImplementedError

    def update(self, borrow_id: int, borrowing: borrowing_schema.BorrowingUpdate) -> Optional[BorrowingManager]:
        raise NotImplementedError

    def delete(self, borrow_id: int) -> bool:
        raise NotImplementedError