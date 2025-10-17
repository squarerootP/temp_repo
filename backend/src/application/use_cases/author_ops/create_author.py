from sqlalchemy.orm import Session

from backend.src.domain.entities.models import Author
from backend.src.presentation.schemas import author_schema
from backend.src.infrastructure.persistence.author_repository_impl import AuthorRepository

def create_author(author_repo: AuthorRepository, author: author_schema.AuthorCreate) -> Author:
    return author_repo.create(author)