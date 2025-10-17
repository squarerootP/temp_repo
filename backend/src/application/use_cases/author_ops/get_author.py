from typing import List, Optional

from sqlalchemy.orm import Session

from backend.src.domain.entities.models import Author
from backend.src.infrastructure.persistence.author_repository_impl import AuthorRepository

def get_author(author_repo: AuthorRepository, author_id: int) -> Optional[Author]:
    return author_repo.get_by_id(author_id)

def get_author_by_email(author_repo: AuthorRepository, email: str) -> Optional[Author]:
    return author_repo.get_by_email(email)

def get_authors(author_repo: AuthorRepository, skip: int = 0, limit: int = 100) -> List[Author]:
    return author_repo.list(skip, limit)
