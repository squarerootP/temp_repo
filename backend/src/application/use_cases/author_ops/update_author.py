from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.src.application.use_cases import author_ops
from backend.src.domain.entities.models import Author
from backend.src.presentation.schemas import author_schema
from backend.src.infrastructure.persistence.author_repository_impl import AuthorRepository


def update_author(author_repo: AuthorRepository, author_id: int, author: author_schema.AuthorUpdate) -> Optional[Author]:
    return author_repo.update(author_id, author)