from datetime import timedelta
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.application.interfaces.borrowing_repository import \
    BorrowingRepository
from backend.src.domain.entities.book import Book
from backend.src.domain.entities.borrowing import BorrowingManager


class BorrowingRepositoryImpl(BorrowingRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, borrowing: BorrowingManager) -> BorrowingManager:
        """Create a new borrowing record and update related book state."""
        try:
            # ensure due_date is set
            if not borrowing.due_date:
                borrowing.due_date = borrowing.borrow_date + timedelta(days=14) #type: ignore

            # Update currently_borrowed_by on Book
            book = (
                self.db.query(Book)
                .filter(Book.isbn == borrowing.book_isbn) #type: ignore
                .first()  # type: ignore
            )
            if book:
                book.currently_borrowed_by = borrowing.user_id

            self.db.add(borrowing)
            self.db.commit()
            self.db.refresh(borrowing)
            return borrowing

        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_by_id(self, borrow_id: int) -> Optional[BorrowingManager]:
        return self.db.query(BorrowingManager).filter(BorrowingManager.borrow_id == borrow_id).first() #type: ignore

    def list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        user_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[BorrowingManager]:
        query = self.db.query(BorrowingManager)
        if user_id:
            query = query.filter(BorrowingManager.user_id == user_id)#type: ignore
        if status:
            query = query.filter(BorrowingManager.status == status)#type: ignore
        return query.offset(skip).limit(limit).all()

    def update(self, borrow_id: int, borrowing: dict) -> Optional[BorrowingManager]:
        db_borrowing = self.get_by_id(borrow_id)
        if not db_borrowing:
            return None
        borrowing_data = borrowing
        for key, value in borrowing_data.items():
            setattr(db_borrowing, key, value)

        # If returned, update Book
        if borrowing_data.get("status") == "returned":
            book = self.db.query(Book).filter(Book.isbn == db_borrowing.book_isbn).first() #type: ignore
            if book and book.currently_borrowed_by == db_borrowing.user_id:
                book.currently_borrowed_by = None

        self.db.commit()
        self.db.refresh(db_borrowing)
        return db_borrowing

    def delete(self, borrow_id: int) -> bool:
        db_borrowing = self.get_by_id(borrow_id)
        if not db_borrowing:
            return False
        self.db.delete(db_borrowing)
        self.db.commit()
        return True