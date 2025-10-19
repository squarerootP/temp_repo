from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.src.application.interfaces.book_repository import BookRepository
from backend.src.domain.entities.models import Author, Book


class BookRepositoryImpl(BookRepository):
    """SQLAlchemy implementation of BookRepository."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        return self.db.query(Book).filter(Book.isbn == isbn).first()

    def list(self, skip: int = 0, limit: int = 100) -> List[Book]:
        return self.db.query(Book).offset(skip).limit(limit).all()

    def save(self, book: Book) -> None:
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return True

    def delete(self, book_id: int) -> None:
        book = self.get_by_isbn(book_id)
        if book:
            self.db.delete(book)
            self.db.commit()
            return True
        return False

    def search(self, text_to_search: str, skip: int = 0, limit: int =100) -> Optional[List[Book]]:

        query = self.db.query(Book).outerjoin(Author).filter(
        or_(
            Book.title.ilike(text_to_search),
            Book.isbn.ilike(text_to_search),
            Book.genre.ilike(text_to_search),
            Book.summary.ilike(text_to_search),
            Author.first_name.ilike(text_to_search),
            Author.last_name.ilike(text_to_search),
            )
        )
        return query.offset(skip).limit(limit).all() if query.count() > 0 else None
    
    def update(self, book_id: int, book_data: dict) -> Optional[Book]:
        db_book = self.get_by_isbn(book_id)
        if not db_book:
            return None
        for key, value in book_data.items():
            setattr(db_book, key, value)
        self.db.commit()
        self.db.refresh(db_book)
        return db_book