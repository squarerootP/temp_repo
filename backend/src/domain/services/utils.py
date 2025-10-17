from datetime import datetime
from typing import Any, Dict, List

from passlib.context import CryptContext
from sqlalchemy import and_
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# def check_for_overdue_books(db: Session) -> List[borrowing_ent.BorrowingManager]:
#     """Check for books that are overdue and update their status"""
#     today = datetime.now()
#     overdue_borrowings = db.query(borrowing_ent.BorrowingManager).filter(
#         and_(
#             borrowing_ent.BorrowingManager.status == "borrowed",
#             borrowing_ent.BorrowingManager.due_date < today
#         )
#     ).all()
    
#     for borrowing in overdue_borrowings:
#         borrowing.status = "overdue"
    
#     db.commit()
#     return overdue_borrowings


# def get_available_books(db: Session, skip: int = 0, limit: int = 100) -> List[book_ent.Book]:
#     """Get books that are currently available (not borrowed)"""
#     return db.query(book_ent.Book).filter(book_ent.Book.currently_borrowed_by == None).offset(skip).limit(limit).all()

# def get_user_statistics(db: Session, user_id: int) -> Dict[str, Any]:
#     """Get statistics for a specific user"""
#     user = get_user_by_id(db, user_id)
#     if not user:
#         return {}
    
#     current_borrowings = db.query(borrowing_ent.BorrowingManager).filter(
#         and_(
#             borrowing_ent.BorrowingManager.user_id == user_id,
#             borrowing_ent.BorrowingManager.status == "borrowed"
#         )
#     ).count()
    
#     overdue_borrowings = db.query(borrowing_ent.BorrowingManager).filter(
#         and_(
#             borrowing_ent.BorrowingManager.user_id == user_id,
#             borrowing_ent.BorrowingManager.status == "overdue"
#         )
#     ).count()
    
#     return {
#         "user_id": user_id,
#         "current_borrowings": current_borrowings,
#         "overdue_borrowings": overdue_borrowings,
#     }