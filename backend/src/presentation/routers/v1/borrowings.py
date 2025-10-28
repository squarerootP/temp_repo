from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.application.use_cases import book_ops, borrowing_ops
from backend.src.domain.entities.library_entities.user import User
from backend.src.domain.exceptions.book_exceptions import BookNotFound
from backend.src.domain.exceptions.borrowing_exceptions import (
    BorrowingNotFoundException, BorrowingNotYetReturnedException)
from backend.src.infrastructure.persistence.database import get_db
from backend.src.infrastructure.persistence.repository_impl.library_repos_impl.book_repository_impl import \
    BookRepositoryImpl
from backend.src.infrastructure.persistence.repository_impl.library_repos_impl.borrowing_repository_impl import \
    BorrowingRepositoryImpl
from backend.src.infrastructure.web.auth_provider import (
    get_current_active_user, has_role)
from backend.src.presentation.schemas.library_schemas import borrowing_schema

router = APIRouter(
    prefix="/borrowings",
    tags=["Borrowings"]
)

@router.post("/", response_model=borrowing_schema.BorrowingResponse, status_code=status.HTTP_201_CREATED)
def create_new_borrowing(
    borrowing: borrowing_schema.BorrowingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new borrowing record.
    - A user can only create a borrowing for themselves (unless they are an admin).
    - A book must be available to be borrowed.
    """
    borrowing_repo = BorrowingRepositoryImpl(db)
    book_repo = BookRepositoryImpl(db)
    if current_user.role != 'admin' and borrowing.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to create a borrowing for another user."
        )

    try:
        db_book = book_ops.get_book_by_isbn(book_repo=book_repo, isbn=borrowing.book_isbn)
        if db_book.currently_borrowed_by is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book is currently unavailable")
    except BookNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ISBN {borrowing.book_isbn} not found")
    try: 
        db_borrowing = borrowing_ops.create_borrowing(borrowing_repo, data=borrowing.model_dump(exclude_unset=True))
    except BorrowingNotYetReturnedException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Book with ISBN {borrowing.book_isbn} is already borrowed and not yet returned.")
    return db_borrowing

@router.get("/", response_model=List[borrowing_schema.BorrowingResponse])
def get_all_borrowings(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    borrow_status: Optional[borrowing_schema.BorrowStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve borrowing records.
    - Admins can view all records and filter by any user.
    - Regular users can only view their own borrowing records.
    """
    borrowing_repo = BorrowingRepositoryImpl(db)
    query_user_id = user_id
    # If a non-admin user is making the request, force the query to their own user_id.
    if current_user.role != 'admin':
        if user_id and user_id != current_user.user_id:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own borrowing records."
            )
        query_user_id = current_user.user_id

    borrowings = borrowing_ops.get_borrowings(borrowing_repo, skip=skip, limit=limit, user_id=query_user_id, status=borrow_status)
    return borrowings

@router.get("/{borrow_id}", response_model=borrowing_schema.BorrowingDetailResponse)
def read_borrowing_record(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a specific borrowing record by its ID.
    - A user can only view their own records, while an admin can view any record.
    """
    borrowing_repo = BorrowingRepositoryImpl(db)
    try:
        db_borrowing = borrowing_ops.get_borrowing(borrowing_repo, borrow_id=borrow_id)
    except BorrowingNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrowing record not found")

    
    # Authorization check
    if current_user.role != 'admin' and db_borrowing.user_id != current_user.user_id: #type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this record."
        )

    return db_borrowing

@router.put("/{borrow_id}", response_model=borrowing_schema.BorrowingResponse)
def update_borrowing_record(
    borrow_id: int,
    borrowing: borrowing_schema.BorrowingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role("admin"))
):
    """
    Update a borrowing record (e.g., change status to 'returned').
    - This action is restricted to admins.
    """
    borrowing_repo = BorrowingRepositoryImpl(db)
    try:
        updated_borrowing = borrowing_ops.update_borrowing(borrowing_repo, borrow_id, data = borrowing.model_dump(exclude_unset=True))
    except BorrowingNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrowing record not found")
    
    return updated_borrowing

@router.delete("/{borrow_id}", status_code=status.HTTP_200_OK)
def remove_borrowing_record(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role("admin"))
):
    """
    Delete a borrowing record.
    - This action is restricted to admins.
    """
    borrowing_repo = BorrowingRepositoryImpl(db)
    try:
        borrowing_ops.delete_borrowing(borrowing_repo, borrow_id)
    except BorrowingNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrowing record not found")
    return {"message": "Borrowing record deleted successfully"}