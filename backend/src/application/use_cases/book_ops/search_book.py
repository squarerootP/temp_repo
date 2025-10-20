from typing import List, Optional

from backend.src.application.interfaces.book_repository import BookRepository
from backend.src.domain.entities.book import Book


def search_books(book_repo: BookRepository, text_to_search: str, skip: int =0, limit: int = 100) -> Optional[List[Book]]:
    """Business logic for searching books."""
    return book_repo.search(text_to_search, skip=skip, limit=limit)