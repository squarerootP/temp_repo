from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.application.use_cases import book_ops
from backend.src.domain.entities.library_entities.user import User
from backend.src.domain.exceptions.book_exceptions import (BookAlreadyExists,
                                                           BookNotFound)
from backend.src.infrastructure.persistence.database import get_db
from backend.src.infrastructure.persistence.repository_impl.library_repos_impl.book_repository_impl import \
    BookRepositoryImpl
from backend.src.infrastructure.web.auth_provider import has_role
from backend.src.presentation.schemas.library_schemas import book_schema

router = APIRouter(
    prefix="/books", 
    tags=["Books"]
)

@router.get("/", response_model=List[book_schema.BookResponse])
def get_all_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):  
    book_repo = BookRepositoryImpl(db)
    books = book_ops.get_books(book_repo, skip=skip, limit=limit)
    return books

@router.get("/search", response_model=List[book_schema.BookResponse])
def search_books(
    text_to_search: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all books with matching information, default to 0-100
    """
    book_repo = BookRepositoryImpl(db)
    books = book_ops.search_books(book_repo, text_to_search=text_to_search, skip=skip, limit=limit)
    return books

@router.get("/{isbn}", response_model=book_schema.BookResponse)
def read_book_by_isbn(
    isbn: str,  
    db: Session = Depends(get_db)
):
    """
    Retrieve a book using its ISBN.
    """
    book_repo = BookRepositoryImpl(db)
    try:    
        db_book = book_ops.get_book_by_isbn(book_repo=book_repo, isbn=isbn)
    except BookNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return db_book

@router.post("/", response_model=book_schema.BookResponse, status_code=status.HTTP_201_CREATED)
def add_book(
    book: book_schema.BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role("admin")),
):
    """
    Add a book to the database.
    """
    book_repo = BookRepositoryImpl(db)
    try:
        return book_ops.create_book(book_repo=book_repo, book_data=book)
    except BookAlreadyExists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book with this ISBN already exists")


@router.put("/{isbn}", response_model=book_schema.BookResponse)
def update_book(
    isbn: str, 
    book: book_schema.BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role("admin")),
):
    """
    Update a book using its ISBN.
    """
    book_repo = BookRepositoryImpl(db)
    try:
        updated_book = book_ops.update_book(book_repo, isbn, book.model_dump(exclude_unset=True))
    except BookNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return updated_book


@router.delete("/{isbn}", status_code=status.HTTP_200_OK)
def delete_book(
    isbn: str,  
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role("admin")),
):
    """
    Delete a book using its ISBN.
    """
    book_repo = BookRepositoryImpl(db)
    try:
        book_ops.delete_book(book_repo, isbn)
    except BookNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return {"message": "Book deleted successfully"}
