from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.domain.entities.library_entities.borrowing import \
    BorrowingManager


class BorrowingRepository(ABC):
    @abstractmethod
    def create(self, borrowing: BorrowingManager) -> BorrowingManager:
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
    def update(self, borrow_id: int, borrowing: dict) -> Optional[BorrowingManager]:
        pass

    @abstractmethod
    def delete(self, borrow_id: int) -> bool:
        pass
    @abstractmethod
    def is_currently_borrowed(self, book_id: str) -> bool:
        pass