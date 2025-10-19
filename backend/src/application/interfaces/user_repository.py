from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def create(self, user: dict) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_phone(self, phone: str) -> Optional[User]:
        pass

    @abstractmethod
    def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        pass

    @abstractmethod
    def search(self, text_to_search: str, skip: int = 0, limit: int = 100) -> List[User]:
        pass

    @abstractmethod
    def update(self, user_id: int, user: dict) -> Optional[User]:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass