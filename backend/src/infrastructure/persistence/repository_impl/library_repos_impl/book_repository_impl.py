from typing import List, Optional, Dict

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.src.application.interfaces.library_interfaces.book_repository import \
    BookRepository
from backend.src.domain.entities.library_entities.book import Book
from backend.src.infrastructure.adapters.mappers.library_mapper.book_mapper import \
    BookMapper
from backend.src.infrastructure.persistence.models.normal_models import \
    BookModel


class BookRepositoryImpl(BookRepository):
    """SQLAlchemy implementation of BookRepository."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_isbn(self, book_isbn: str) -> Optional[Book]:
        db_book = (
            self.db.query(BookModel).filter(BookModel.book_isbn == book_isbn).first()
        )
        return BookMapper.to_entity(db_book) if db_book else None

    def list(self, skip: int = 0, limit: int = 100) -> List[Book]:
        db_books = self.db.query(BookModel).offset(skip).limit(limit).all()
        return [BookMapper.to_entity(book) for book in db_books]

    def save(self, book: Book) -> Book:
        db_book = BookMapper.to_model(book)
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        return book

    def delete(self, book_isbn: str) -> bool:
        db_book = (
            self.db.query(BookModel).filter(BookModel.book_isbn == book_isbn).first()
        )

        if db_book:
            self.db.delete(db_book)
            self.db.commit()
            return True
        return False

    def search(
        self, text_to_search: str, skip: Optional[int] = 0, limit: Optional[int] = 100
    ) -> Optional[List[Book]]:
        search_pattern = f"%{text_to_search}%"
        query = (
            self.db.query(BookModel)
            .filter(
                or_(
                    BookModel.title.ilike(search_pattern),
                    BookModel.book_isbn.ilike(search_pattern),
                    BookModel.genre.ilike(search_pattern),
                    BookModel.summary.ilike(search_pattern),
                )
            )
        )
        db_books = query.offset(skip).limit(limit).all()

        if not db_books:
            return None

        return [BookMapper.to_entity(book) for book in db_books]

    def update(self, book_isbn: str, book_data: dict) -> Optional[Book]:
        db_book = (
            self.db.query(BookModel).filter(BookModel.book_isbn == book_isbn).first()
        )

        if not db_book:
            return None

        for key, value in book_data.items():
            setattr(db_book, key, value)

        self.db.commit()
        self.db.refresh(db_book)

        return BookMapper.to_entity(db_book)
    
    def get_all_authors(self) -> List[str]:
        """Retrieve a list of all authors in the repository."""
        authors = (
            self.db.query(BookModel.author_name)
            .distinct()
            .all()
        )
        return [author[0] for author in authors if author[0] is not None]
    
    def get_all_genres(self) -> List[str]:
        """Retrieve a list of all genres in the repository."""
        genres = (
            self.db.query(BookModel.genre)
            .distinct()
            .all()
        )
        return [genre[0] for genre in genres if genre[0] is not None]
    
    def get_books_with_filter(
        self,
        genre: Optional[List[str]],
        author: Optional[List[str]],
        title: Optional[str],
        published_year: Optional[int | Dict[str, int]]
    ) -> List[Book]:
        """
        Retrieve books filtered by genre, author, title, or publication year (exact or range).
        """
        query = self.db.query(BookModel)

        # Genre filter (multiple)
        if genre:
            query = query.filter(BookModel.genre.in_(genre))

        # Author filter (multiple)
        if author:
            query = query.filter(BookModel.author_name.in_(author))

        # Title filter (case-insensitive partial match)
        if title:
            query = query.filter(BookModel.title.ilike(f"%{title}%"))

        # Published year filter (exact or range)
        if published_year:
            if isinstance(published_year, dict):
                start = published_year.get("from")
                end = published_year.get("to")
                if start and end:
                    query = query.filter(BookModel.published_year.between(start, end))
                elif start:
                    query = query.filter(BookModel.published_year >= start)
                elif end:
                    query = query.filter(BookModel.published_year <= end)
            else:
                query = query.filter(BookModel.published_year == published_year)

        db_books = query.all()
        return [BookMapper.to_entity(book) for book in db_books]
