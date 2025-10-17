from typing import Optional

from sqlalchemy.orm import Session

from backend.src.application.use_cases import book_ops
from backend.src.domain.entities.models import Book
from backend.src.presentation.schemas.book_schema import BookUpdate
from backend.src.application.interfaces.book_repository import BookRepository

def update_book(book_repo: BookRepository, book_id: int, book_data: BookUpdate) -> Optional[Book]:
    """Business logic for updating a book."""
    book_data = book_data.model_dump()
    return book_repo.update(book_id, book_data)