from datetime import timedelta
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.application.interfaces.borrowing_repository import \
    BorrowingRepository
from backend.src.domain.entities.borrowing import BorrowingManager
from backend.src.infrastructure.adapters.mappers.borrowing_mapper import \
    BorrowingManagerMapper
from backend.src.infrastructure.persistence.models.normal_models import (
    BookModel, BorrowingManagerModel)


class BorrowingRepositoryImpl(BorrowingRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, borrowing: BorrowingManager) -> BorrowingManager:
        """Create a new borrowing record and update related book state."""
        try:
            # Convert entity to model
            db_borrowing = BorrowingManagerMapper.to_model(borrowing)
            
            # ensure due_date is set
            if db_borrowing.due_date is None:
                db_borrowing.due_date = db_borrowing.borrow_date + timedelta(days=14)

            # Update currently_borrowed_by on Book
            book = (
                self.db.query(BookModel)
                .filter(BookModel.book_isbn == db_borrowing.book_isbn)
                .first()
            )
            if book:
                book.currently_borrowed_by = db_borrowing.user_id

            self.db.add(db_borrowing)
            self.db.commit()
            self.db.refresh(db_borrowing)
            
            # Convert back to entity
            return BorrowingManagerMapper.to_entity(db_borrowing)

        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_by_id(self, borrow_id: int) -> Optional[BorrowingManager]:
        db_borrowing = self.db.query(BorrowingManagerModel).filter(
            BorrowingManagerModel.borrow_id == borrow_id
        ).first()
        
        return BorrowingManagerMapper.to_entity(db_borrowing) if db_borrowing else None

    def list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        user_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[BorrowingManager]:
        query = self.db.query(BorrowingManagerModel)
        if user_id:
            query = query.filter(BorrowingManagerModel.user_id == user_id)
        if status:
            query = query.filter(BorrowingManagerModel.status == status)
        db_borrowings = query.offset(skip).limit(limit).all()
        
        return [BorrowingManagerMapper.to_entity(borrowing) for borrowing in db_borrowings]

    def update(self, borrow_id: int, borrowing: dict) -> Optional[BorrowingManager]:
        db_borrowing = self.db.query(BorrowingManagerModel).filter(
            BorrowingManagerModel.borrow_id == borrow_id
        ).first()
        
        if not db_borrowing:
            return None
            
        for key, value in borrowing.items():
            setattr(db_borrowing, key, value)

        # If returned, update Book
        if borrowing.get("status") == "returned":
            book = self.db.query(BookModel).filter(BookModel.book_isbn == db_borrowing.book_isbn).first()
            if book is not None and book.currently_borrowed_by == db_borrowing.user_id:
                book.currently_borrowed_by = None

        self.db.commit()
        self.db.refresh(db_borrowing)
        
        return BorrowingManagerMapper.to_entity(db_borrowing)

    def delete(self, borrow_id: int) -> bool:
        db_borrowing = self.db.query(BorrowingManagerModel).filter(
            BorrowingManagerModel.borrow_id == borrow_id
        ).first()
        
        if not db_borrowing:
            return False
            
        self.db.delete(db_borrowing)
        self.db.commit()
        return True

    def is_currently_borrowed(self, book_id: str) -> bool:
        result = self.db.query(BorrowingManagerModel).filter(
            BorrowingManagerModel.book_isbn == book_id,
            BorrowingManagerModel.status == "borrowed"
        ).first()
        return result is not None