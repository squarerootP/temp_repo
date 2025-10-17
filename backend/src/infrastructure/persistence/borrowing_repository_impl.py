from datetime import timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.src.domain.entities.models import BorrowingManager, Book
from backend.src.presentation.schemas import borrowing_schema
from backend.src.application.interfaces.borrowing_repository import BorrowingRepository

class BorrowingRepositoryImpl(BorrowingRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, borrowing: borrowing_schema.BorrowingCreate) -> BorrowingManager:
        # Set due date if missing
        borrowing_dict = borrowing.model_dump()
        if not borrowing.due_date:
            borrowing_dict["due_date"] = borrowing.borrow_date + timedelta(days=14)
        db_borrowing = BorrowingManager(**borrowing_dict)
        
        # Update currently_borrowed_by on Book
        book = self.db.query(Book).filter(Book.isbn == borrowing.book_isbn).first()
        if book:
            book.currently_borrowed_by = borrowing.user_id
        
        self.db.add(db_borrowing)
        self.db.commit()
        self.db.refresh(db_borrowing)
        return db_borrowing

    def get_by_id(self, borrow_id: int) -> Optional[BorrowingManager]:
        return self.db.query(BorrowingManager).filter(BorrowingManager.borrow_id == borrow_id).first()

    def list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        user_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[BorrowingManager]:
        query = self.db.query(BorrowingManager)
        if user_id:
            query = query.filter(BorrowingManager.user_id == user_id)
        if status:
            query = query.filter(BorrowingManager.status == status)
        return query.offset(skip).limit(limit).all()

    def update(self, borrow_id: int, borrowing: borrowing_schema.BorrowingUpdate) -> Optional[BorrowingManager]:
        db_borrowing = self.get_by_id(borrow_id)
        if not db_borrowing:
            return None
        borrowing_data = borrowing.model_dump(exclude_unset=True)
        for key, value in borrowing_data.items():
            setattr(db_borrowing, key, value)

        # If returned, update Book
        if borrowing_data.get("status") == "returned":
            book = self.db.query(Book).filter(Book.isbn == db_borrowing.book_isbn).first()
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