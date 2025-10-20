from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.application.use_cases import author_ops
from backend.src.domain.entities.user import User
from backend.src.domain.exceptions.author_exceptions import (
    AuthorEmailAlreadyRegistered, AuthorNotFound)
from backend.src.infrastructure.persistence.database import get_db
from backend.src.infrastructure.persistence.repository_impl.author_repository_impl import \
    AuthorRepositoryImpl
from backend.src.infrastructure.web.auth_provider import has_role
from backend.src.presentation.schemas import author_schema

router = APIRouter(
    prefix="/authors",
    tags=["Authors"]
)

@router.get("/", response_model=List[author_schema.AuthorResponse])
def get_all_authors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all authors, with pagination.
    """
    author_repo = AuthorRepositoryImpl(db)
    authors = author_ops.get_authors(author_repo, skip=skip, limit=limit)
    return authors

@router.get("/search", response_model=List[author_schema.AuthorResponse])
def search_for_authors(
    text_to_search: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all authors with matching information.
    """
    author_repo = AuthorRepositoryImpl(db)
    authors = author_ops.search_authors(author_repo, text_to_search=text_to_search, skip=skip, limit=limit)
    return authors

@router.get("/{author_id}", response_model=author_schema.AuthorResponse)
def read_author(
    author_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve an author using their ID.
    """
    author_repo = AuthorRepositoryImpl(db)
    try:
        db_author = author_ops.get_author(author_repo, author_id=author_id)
    except AuthorNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with id {author_id} not found")
    return db_author

@router.post("/", response_model=author_schema.AuthorResponse, status_code=status.HTTP_201_CREATED)
def add_author(
    author: author_schema.AuthorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role("admin")),
):
    """
    Add an author to the database. Only accessible by admins.
    """
    author_repo = AuthorRepositoryImpl(db)
    try:
        author_ops.create_author(author_repo, author=author.model_dump(exclude_unset=True))
    except AuthorEmailAlreadyRegistered:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author with this email already exists")
    return True

@router.put("/{author_id}", response_model=author_schema.AuthorResponse)
def update_author_details(
    author_id: int,
    author: author_schema.AuthorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role("admin")),
):
    """
    Update an author using their ID. Only accessible by admins.
    """
    author_repo = AuthorRepositoryImpl(db)
    try:
        updated_author = author_ops.update_author(author_repo, author_id, author.model_dump(exclude_unset=True))
    except AuthorNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with id {author_id} not found")
    return updated_author

@router.delete("/{author_id}", status_code=status.HTTP_200_OK)
def remove_author(
    author_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role("admin")),
):
    """
    Delete an author using their ID. Only accessible by admins.
    """
    author_repo = AuthorRepositoryImpl(db)
    try:
        author_ops.delete_author(author_repo, author_id)
    except AuthorNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with id {author_id} not found")
    return {"message": "Author deleted successfully"}