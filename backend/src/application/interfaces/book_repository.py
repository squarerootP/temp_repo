from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.domain.entities.book import Book


class BookRepository(ABC):
    """Abstract interface for Book persistence operations."""
    
    @abstractmethod
    def get_by_isbn(self, book_id: int) -> Optional[Book]:
        """Retrieve a Book by its primary key."""
        pass
    
    @abstractmethod
    def search(self, text_to_search: str, skip: int, limit: int) -> Optional[List[Book]]:
        """Retrieve list of Books that match the search string"""
        pass

    @abstractmethod
    def list(self, skip: int = 0, limit: int = 100) -> List[Book]:
        """List all books with pagination."""
        pass

    @abstractmethod
    def save(self, book: Book) -> None:
        """Add or update a Book record."""
        pass

    @abstractmethod
    def delete(self, book_id: int) -> None:
        """Delete a Book by its ID."""
        pass
    
    @abstractmethod
    def update(self, book_id: int, book_data: dict) -> Optional[Book]:
        pass