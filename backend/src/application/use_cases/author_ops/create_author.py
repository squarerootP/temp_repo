from typing import Optional

from backend.src.application.interfaces.author_repository import \
    AuthorRepository
from backend.src.domain.entities.author import Author


def create_author(author_repo: AuthorRepository, author: dict) -> Optional[Author]:
    email = author["email"]
    if author_repo.get_by_email(email):
        raise ValueError("Author email already registered")

    author_entity = Author(**author)
    return author_repo.create(author_entity)