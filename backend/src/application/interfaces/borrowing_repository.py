from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.domain.entities.borrowing import BorrowingManager
from backend.src.presentation.schemas import borrowing_schema


class BorrowingRepository(ABC):
    @abstractmethod
    def create(self, borrowing: borrowing_schema.BorrowingCreate) -> BorrowingManager:
        pass

    @abstractmethod
    def get_by_id(self, borrow_id: int) -> Optional[BorrowingManager]:
        pass

    @abstractmethod
    def list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        user_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[BorrowingManager]:
        pass

    @abstractmethod
    def update(self, borrow_id: int, borrowing: borrowing_schema.BorrowingUpdate) -> Optional[BorrowingManager]:
        pass

    @abstractmethod
    def delete(self, borrow_id: int) -> bool:
        pass