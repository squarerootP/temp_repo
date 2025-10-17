from typing import List, Optional
from backend.src.domain.entities.models import Book

class BookRepository:
    """Abstract interface for Book persistence operations."""
    
    def get_by_isbn(self, book_id: int) -> Optional[Book]:
        """Retrieve a Book by its primary key."""
        raise NotImplementedError
    def search(self, text_to_search: str, skip: int, limit: int) -> Optional[List[Book]]:
        """Retrieve list of Books that match the search string"""
        raise NotImplementedError

    def list(self, skip: int = 0, limit: int = 100) -> List[Book]:
        """List all books with pagination."""
        raise NotImplementedError

    def save(self, book: Book) -> None:
        """Add or update a Book record."""
        raise NotImplementedError

    def delete(self, book_id: int) -> None:
        """Delete a Book by its ID."""
        raise NotImplementedError
    def update(self, book_id: int, book_data: dict) -> Optional[Book]:
        raise NotImplementedError