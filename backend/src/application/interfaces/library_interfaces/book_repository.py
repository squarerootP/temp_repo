from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from backend.src.domain.entities.library_entities.book import Book


class BookRepository(ABC):
    """Abstract interface for Book persistence operations."""

    @abstractmethod
    def get_by_isbn(self, book_isbn: str) -> Optional[Book]:
        """Retrieve a Book by its primary key."""
        pass

    @abstractmethod
    def search(
        self, text_to_search: str, skip: Optional[int], limit: Optional[int]
    ) -> Optional[List[Book]]:
        """Retrieve list of Books that match the search string"""
        pass

    @abstractmethod
    def list(self, skip: int = 0, limit: int = 100) -> List[Book]:
        """List all books with pagination."""
        pass

    @abstractmethod
    def save(self, book: Book) -> Book:
        """Add or update a Book record."""
        pass

    @abstractmethod
    def delete(self, book_isbn: str) -> bool:
        """Delete a Book by its ID."""
        pass

    @abstractmethod
    def update(self, book_isbn: str, book_data: dict) -> Optional[Book]:
        pass

    @abstractmethod
    def get_all_authors(self) -> List[str]:
        """Retrieve a list of all authors in the repository."""
        pass
    
    @abstractmethod
    def get_all_genres(self) -> List[str]:
        """Retrieve a list of all genres in the repository."""
        pass

    @abstractmethod
    def get_books_with_filter(self, genre: Optional[List[str]], author: Optional[List[str]], title: Optional[str], published_year: Optional[int | Dict[str, int]]
                              ) -> List[Book]:
        """Retrieve books filtered by genre and/or author."""
        pass