from typing import List, Optional

from sqlalchemy.orm import Session

from backend.src.application.interfaces.author_repository import \
    AuthorRepository
from backend.src.domain.entities.author import Author
from backend.src.domain.exceptions.author_exceptions import AuthorNotFound


def get_author(author_repo: AuthorRepository, author_id: int) -> Optional[Author]:
    author = author_repo.get_by_id(author_id=author_id)
    if not author:
        raise AuthorNotFound.by_id(author_id)
    return author

def get_author_by_email(author_repo: AuthorRepository, email: str) -> Optional[Author]:
    author = author_repo.get_by_email(email=email)
    if not author:
        raise AuthorNotFound.by_email(email)
    return author

def get_authors(author_repo: AuthorRepository, skip: int = 0, limit: int = 100) -> List[Author]:
    author_lst = author_repo.list(skip=skip, limit=limit)
    if not author_lst:
        raise AuthorNotFound("No authors found.")
    return author_lst
