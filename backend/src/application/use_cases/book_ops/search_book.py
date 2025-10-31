from typing import List, Optional

from backend.src.application.interfaces.library_interfaces.book_repository import \
    BookRepository
from backend.src.domain.entities.library_entities.book import Book


class SearchBookUseCase:
    def __init__(self, book_repo: BookRepository):
        self.book_repo = book_repo

    def execute(
        self,
        text_to_search: str,
        skip: Optional[int | None] = 0,
        limit: Optional[int | None] = 100,
    ) -> Optional[List[Book]]:
        """Business logic for searching books."""
        return self.book_repo.search(
            text_to_search=text_to_search, skip=skip, limit=limit
        )
