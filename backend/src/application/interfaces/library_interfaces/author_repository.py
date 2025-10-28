from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.domain.entities.library_entities import Author


class AuthorRepository(ABC):
    @abstractmethod
    def create(self, author: Author) -> Author:
        pass

    @abstractmethod
    def get_by_id(self, author_id: int) -> Optional[Author]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Author]:
        pass

    @abstractmethod
    def list(self, skip: int = 0, limit: int = 100) -> List[Author]:
        pass

    @abstractmethod
    def search(self, text_to_search: str, skip: int = 0, limit: int = 100) -> List[Author]:
        pass

    @abstractmethod
    def update(self, author_id: int, author: dict) -> Optional[Author]:
        pass

    @abstractmethod
    def delete(self, author_id: int) -> bool:
        pass
