from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.src.application.interfaces.book_repository import BookRepository
from backend.src.domain.entities.author import Author
from backend.src.domain.entities.book import Book


class BookRepositoryImpl(BookRepository):
    """SQLAlchemy implementation of BookRepository."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_isbn(self, book_isbn: str) -> Optional[Book]:
        return self.db.query(Book).filter(Book.isbn == book_isbn).first() #type: ignore

    def list(self, skip: int = 0, limit: int = 100) -> List[Book]:
        return self.db.query(Book).offset(skip).limit(limit).all()

    def save(self, book: Book) -> bool:
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return True

    def delete(self, book_isbn: str) -> bool:
        book = self.get_by_isbn(book_isbn)
        if book:
            self.db.delete(book)
            self.db.commit()
            return True
        return False

    def search(self, text_to_search: str, skip: int = 0, limit: int =100) -> Optional[List[Book]]:

        query = self.db.query(Book).outerjoin(Author).filter(
        or_(
            Book.title.ilike(text_to_search), #type: ignore
            Book.isbn.ilike(text_to_search), #type: ignore
            Book.genre.ilike(text_to_search), #type: ignore
            Book.summary.ilike(text_to_search), #type: ignore
            Author.first_name.ilike(text_to_search), #type: ignore
            Author.last_name.ilike(text_to_search), #type: ignore
            )
        )
        return query.offset(skip).limit(limit).all() if query.count() > 0 else None
    
    def update(self, book_isbn: str, book_data: dict) -> Optional[Book]:
        db_book = self.get_by_isbn(book_isbn)
        if not db_book:
            return None
        for key, value in book_data.items():
            setattr(db_book, key, value)
        self.db.commit()
        self.db.refresh(db_book)
        return db_book